from __future__ import print_function
from fnmatch import fnmatch
from copy import deepcopy

class PathNotFoundError(KeyError):
    pass

class GenClause(object):

    ACCESS_ANY = -1
    ACCESS_ALL = -2
    ACCESS_ONE = -3

    def __init__(self, left):
        self.left = left
        self.operator = ''
        self.right = None

    def __eq__(self, other):
        self.operator = '=='
        self.right = other
        return self

    def __ne__(self, other):
        self.operator = '!='
        self.right = other
        return self

    def __le__(self, other):
        self.operator = '<='
        self.right = other
        return self

    def __lt__(self, other):
        self.operator = '<'
        self.right = other
        return self

    def __ge__(self, other):
        self.operator = '>='
        self.right = other
        return self

    def __gt__(self, other):
        self.operator = '>'
        self.right = other
        return self

    def __nonzero__(self):
        self.operator = 'if'
        self.right = ''
        return self

    def in_(self, *args):
        self.operator = 'in'
        if isinstance(args[0], self.__class__):
            self.right = args[0]
        else:
            self.right = args
        return self

    def is_(self, other):
        self.operator = 'is'
        self.right = other
        return self

    def like(self, other):
        self.operator = 'like'
        self.right = other
        return self

    @staticmethod
    def extractValue(row, path):
        #print("extractValue", row, path)

        if not isinstance(path, basestring):
            return (path, GenClause.ACCESS_ONE)

        if path[0] in ('"',"'"):
            return (path[1:-1], GenClause.ACCESS_ONE)

        if '.' in path:
            parts = path.split('.')
            child, access = GenClause.extractValue(row, parts[0])

            if access == GenClause.ACCESS_ONE:
                return GenClause.extractValue(child, ".".join(parts[1:]))
            elif access in (GenClause.ACCESS_ALL, GenClause.ACCESS_ANY):
                result = []
                try:
                    for item in child:
                        result.append(GenClause.extractValue(item, ".".join(parts[1:]))[0])
                    return result,access
                except TypeError:
                    return None, GenClause.ACCESS_ONE

        if path[-1:] == ']':
            nodeSplit = path.split('[')
            nodeName = nodeSplit[0]
            childs, access = GenClause.extractValue(row, nodeName)
            return (childs, GenClause.ACCESS_ANY)
        try:
            return (row[path], GenClause.ACCESS_ONE)
        except KeyError:
            raise PathNotFoundError()
        except TypeError:
            try:
                return (row.__getattribute__(path), GenClause.ACCESS_ONE)
            except AttributeError:
                raise PathNotFoundError()

    def match(self, row):
        try:
            if isinstance(self.right, self.__class__):
                right, access = self.right.extractValue(row, self.right.left)
            else:
                right = self.right

            left, access = self.extractValue(row, self.left)

            if access is GenClause.ACCESS_ONE:
                return self._matchValue(left, self.operator, right)
            if access is GenClause.ACCESS_ANY:
                for value in left:
                    if self._matchValue(value, self.operator, right):
                        return True
                return False
        except PathNotFoundError:
            return False

    def _matchValue(self, left, operator, right):
        if operator == '==':
            return left == right
        elif operator == '!=':
            return left != right
        elif operator == '<=':
            return left <= right
        elif operator == '<':
            return left < right
        elif operator == '>=':
            return left >= right
        elif operator == '>':
            return left > right
        elif operator == 'if':
            if left:
                return True
            return False
        elif operator == 'in':
            try:
                return left in right
            except TypeError:
                return False
        elif operator == 'is':
            return left is right
        elif operator == 'like':
            return fnmatch(unicode(left).lower(),
                           unicode(right).lower().replace('%','*'))
        raise SyntaxError('Unknown operator ' + operator)

    def __str__(self):
        return u"{0} {1} {2}".format(self.left, self.operator, self.right)
    
    def collect_fieldnames(self):
        fieldNames = set()
        if isinstance(self.left, basestring):
            fieldNames.add(self.left)
        elif hasattr(self.left,'collect_fieldnames'):
            for fieldName in self.left.collect_fieldnames():
                fieldNames.add(fieldName)
        if hasattr(self.right,'collect_fieldnames'):
            for fieldName in self.right.collect_fieldnames():
                fieldNames.add(fieldName)
        return fieldNames


def c(left):
    return GenClause(left)

class Conjunction(object):
    conj_type = 'AND'
    parts = []

    def __init__(self, args=None, conj_type='AND'):
        self.conj_type = conj_type
        self.parts = []
        if args is not None:
            for arg in args:
                self.parts.append(arg)

    def match(self, row):

        if self.conj_type == 'AND':
            for clause in self.parts:
                if not clause.match(row):
                    return False;
            return True
        if self.conj_type == 'OR':
            for clause in self.parts:
                if clause.match(row):
                    return True;
            return False

    def collect_clauses(self):
        result = []
        for part in self.parts:
            if isinstance(part, GenClause):
                result.append(part)
            if isinstance(part, Conjunction):
                for part2 in part.collect_clauses():
                    result.append(part2)
        return result

    def append(self, clause):
        self.parts.append(clause)

    def __len__(self):
        return len(self.parts)


def and_(*args):
    return Conjunction(args, 'AND')

def or_(*args):
    return Conjunction(args, 'OR')


class _SqlIterator(object):

    _query = None
    _where = None

    def __init__(self, query, where=None):
        self._query = query
        self._where = where
        self.reset()

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        row = self._srcIterator.next()
        if self._where.match(row):
            if not self._query.has_fields():
                return row
            else:
                values = {}
                for item in self._query._select:
                    values[item] = GenClause.extractValue(row, item)[0]
                return values
        return self.next()

    def first(self):
        self.reset()
        try:
            return self.next()
        except StopIteration:
            return None

    def last(self):
        self.reset()
        try:
            while True:
                row = self.next()
        except StopIteration:
            try:
                return row
            except UnboundLocalError:
                return None

    def all(self):
        self.reset()
        rows = []
        try:
            while True:
                rows.append(self.next())
        except StopIteration:
            return rows

    def reset(self):
        self._srcIterator = self._query._src.__iter__()

class AlwaysTrueMatcher(object):
    def match(self, row):
        return True

class SqlIterQuery(object):

    _where = None
    _src = []
    _select = None
    _group_by = None

    def __init__(self, *args):
        self._where = None
        self._select = None
        self._where = AlwaysTrueMatcher()
        self._group_by = None
        self.fields(*args)

    def fields(self, *args):
        if not len(args):
            return self._select

        self._select = []

        if isinstance(args[0],(list, tuple, set)):
            for field in args[0]:
                self._select.append(field)
        elif args[0] is None:
            self._select = None
        else:
            for field in args:
                self._select.append(field)

    def group_by(self, *args):
        if not len(args):
            return self._group_by

        self._group_by = []

        if isinstance(args[0],(list, tuple, set)):
            for field in args[0]:
                self._group_by.append(field)
        elif args[0] is None:
            self._group_by = None
        else:
            for field in args:
                self._group_by.append(field)
        return self

    def has_group_by(self):
        return not self._group_by is None

    def has_fields(self):
        if self._select is None:
            return False
        if self._select == ['*']:
            return False
        if len(self._select):
            return True
        return False

    def from_(self, src):
        self._src = src
        return self

    def where(self, *args, **kwargs):
        if kwargs and args:
            raise SyntaxError('User either args or kwargs')
        if kwargs:
            self._where = and_()
            for kw in kwargs:
                self._where.parts.append(c(kw) == kwargs[kw])
        elif len(args):
            if not isinstance(args[0], Conjunction):
                self._where = and_()
                for part in args:
                    self._where.parts.append(part)
            else:
                self._where = args[0]
        else:
            self._where = AlwaysTrueMatcher()
        return self

    def has_where(self):
        return not isinstance(self._where, AlwaysTrueMatcher)

    def has_filter(self):
        return self.has_where()

    def __iter__(self):
        return _SqlIterator(self, self._where)
        #for row in self._src:
            #if self._where.match(row):
                #yield row

    def collect_fieldnames(self):
        fieldNames = set()
        if self.has_fields():
            for field in self._select:
                if isinstance(field, basestring):
                    fieldNames.add(field)
        for fieldName in self.where_fieldnames():
            fieldNames.add(fieldName)
        for fieldName in self.group_by_fieldnames():
            fieldNames.add(fieldName)
        return fieldNames

    def where_fieldnames(self):
        fieldNames = set()
        if self.has_where():
            for clause in self._where.collect_clauses():
                if hasattr(clause,'collect_fieldnames'):
                    for field in clause.collect_fieldnames():
                        fieldNames.add(field)
        return fieldNames

    def group_by_fieldnames(self):
        fieldNames = set()
        if self.has_group_by():
            for field in self._group_by:
                if hasattr(field,'collect_fieldnames'):
                    for fieldName in field.collect_fieldnames():
                        fieldNames.add(fieldName)
                elif isinstance(field,basestring):
                    fieldNames.add(field)
        return fieldNames

    def first(self):
        return self.__iter__().first()

    def last(self):
        return self.__iter__().last()

    def all(self):
        return self.__iter__().all()

    def match(self, data):
        return self._where.match(data)

def select(*args):
    return SqlIterQuery(*args)

def test(*args, **kwargs):
    query = SqlIterQuery(None)
    return query.where(*args, **kwargs)

if __name__ == '__main__':
    #from tests.testdata import dictData
    from tests.testdata import objectData
    dictData = objectData

    matchTest = {'name':'Olaf','weight':67.3,'age':33,'married':True}

    def dev_null(self, *args):
        pass

    printOut = True

    if printOut:
        print_func = print
    else:
        print_func = dev_null
    
    print_func('-------- SELECT FROM dictData')
    for name in select().from_(dictData):
        print_func(name)
    print_func('-------- SELECT FROM dictData WHERE forename = Marc')
    for name in select().from_(dictData).where(forename='Marc'):
        print_func(name)
    print_func('-------- SELECT FROM dictData WHERE surname IN ("Meyer","Muscels")')
    for name in select().from_(dictData).where(c('surname').in_('Meyer','Muscels')):
        print_func(name)
    print_func('-------- SELECT FROM dictData WHERE age > 32')
    for name in select().from_(dictData).where(c('age') > 32):
        print_func(name)
    print_func('-------- SELECT FROM dictData WHERE forname=surname')
    for name in select().from_(dictData).where(c('forename') == c('surname')):
        print_func(name)
    print_func('-------- SELECT FROM dictData WHERE forname=surname OR age < 20')
    for name in select().from_(dictData).where(or_(c('forename') == c('surname'),c('age') < 20)):
        print_func(name)
    print_func('-------- SELECT FROM dictData WHERE forname="Marc" AND surname == "Andrew"')
    for name in select().from_(dictData).where(and_(c('forename') == 'Marc',c('surname') == 'Andrew')):
        print_func(name)
    print_func('-------- SELECT FROM dictData WHERE "family" IN tags')
    for name in select().from_(dictData).where(c('"family"').in_(c('tags'))):
        print_func(name)
    print_func('-------- SELECT FROM dictData WHERE job.name == "President"')
    for name in select().from_(dictData).where(c('job.name') == 'President'):
        print_func(name)
    print_func('-------- SELECT FROM dictData WHERE job.category == "Business"')
    for name in select().from_(dictData).where(c('job.category') == 'Business'):
        print_func(name)
    print_func('-------- SELECT FROM dictData WHERE job.category IN ("Business", "Social")')
    for name in select().from_(dictData).where(c('job.category').in_('Business','Social')):
        print_func(name)
    print_func('-------- SELECT FROM dictData WHERE hobbies[*].name == "reading"')
    for name in select().from_(dictData).where(c('hobbies[*].name') == "reading"):
        print_func(name)
    print_func('-------- SELECT FROM dictData WHERE hobbies[*].period < 7')
    for name in select().from_(dictData).where(c('hobbies[*].period') < 7):
        print_func(name)
    print_func('-------- SELECT FROM dictData WHERE asdkuh < 7')
    for name in select().from_(dictData).where(c('asdkuh') < 7):
        print_func(name)
    print_func('-------- SELECT FROM dictData WHERE hobbies[*].period < 7.first()')
    print_func(select().from_(dictData).where(c('hobbies[*].period') < 7).first())
    print_func('-------- SELECT FROM dictData WHERE hobbies[*].period < 7.last()')
    print_func(select().from_(dictData).where(c('hobbies[*].period') < 7).last())

    print_func('-------- TEST IF age > 22')
    print_func(test(c('age') > 22).match(matchTest))
    print_func('-------- TEST IF age < 22')
    print_func(test(c('age') < 22).match(matchTest))
    print_func('-------- TEST IF name == "Olaf"')
    print_func(test(c('name') == 'Olaf').match(matchTest))
    print_func('-------- TEST IF name != "Olaf"')
    print_func(test(c('name') != 'Olaf').match(matchTest))
    print_func('-------- TEST IF name == "Olafs"')
    print_func(test(c('name') == 'Olafs').match(matchTest))
    print_func('-------- TEST IF name LIKE "Ol%"')
    print_func(test(c('name').like('Ol%')).match(matchTest))
    print_func('-------- TEST IF name LIKE "%laf"')
    print_func(test(c('name').like('%laf')).match(matchTest))
    print_func('-------- TEST IF name LIKE "O%f"')
    print_func(test(c('name').like('O%f')).match(matchTest))
    print_func('-------- TEST IF name LIKE "olaf"')
    print_func(test(c('name').like('olaf')).match(matchTest))

    print_func('-------- SELECT * FROM dictData WHERE job.category IN ("Business", "Social")')
    for name in select('*').from_(dictData).where(c('job.category').in_('Business','Social')):
        print_func(name)

    print_func('-------- SELECT forname FROM dictData WHERE job.category IN ("Business", "Social")')
    for name in select('forename').from_(dictData).where(c('job.category').in_('Business','Social')):
        print_func(name)

    print_func('-------- SELECT forname,tags FROM dictData')
    for name in select('forename','tags').from_(dictData):
        print_func(name)

    print_func('-------- SELECT age FROM dictData WHERE forname="Marc" AND (surname == "Andrew" OR age < size).collect_fieldnames')
    print_func(select('age').from_(dictData).where(and_(c('forename') == 'Marc',or_(c('surname') == 'Andrew'),c('age') < c('size'))).collect_fieldnames())

    print_func('-------- SELECT age FROM dictData WHERE forname="Marc" AND (surname == "Andrew" OR age < size).where_fieldnames')
    print_func(select('age').from_(dictData).where(and_(c('forename') == 'Marc',or_(c('surname') == 'Andrew'),c('age') < c('size'))).where_fieldnames())

    print_func('-------- SELECT age FROM dictData WHERE forname="Marc" AND (surname == "Andrew" OR age < size) GROUP BY tags[0],tags[1]).collect_fieldnames')
    print_func(select('age').from_(dictData).where(
        and_(c('forename') == 'Marc',
             or_(c('surname') == 'Andrew'),c('age') < c('size')
        )).group_by('tags[0]','tags[1]').collect_fieldnames())