
from __future__ import print_function

dictData = [
            {'forename':'Marc','surname':'Mine','age':35, 'tags':('family','work'),
                'job':{'name':'Baker','category':'Business'},
                'hobbies':[{'name':'swimming','period':7},
                           {'name':'reading','period':1}]},
            {'forename':'Mike','surname':'Meyer','age':14, 'tags':('work',),
                'job':{'name':'Banker','category':'Business'},
                'hobbies':[{'name':'swimming','period':14}]},
            {'forename':'Marc','surname':'Andrew','age':78, 'tags':('hobby','work'),
                'job':{'name':'Police','category':'Government'},
                'hobbies':[{'name':'swimming','period':7},
                           {'name':'music','period':1},
                           {'name':'reading','period':2}]},
            {'forename':'Marc','surname':'Muscels','age':35, 'tags':('family','hobby'),
                'job':{'name':'Teacher','category':'Social'},
                'hobbies':[{'name':'math','period':30},
                           {'name':'ski','period':365}]},
            {'forename':'Andy','surname':'Young','age':11, 'tags':('family','work'),
                'job':{'name':'President','category':'Government'},
                'hobbies':[{'name':'swimming','period':2},
                           {'name':'fitness','period':3},
                           {'name':'reading','period':4},
                           {'name':'rc-cars','period':14}]},
            {'forename':'Andy','surname':'Andy','age':51, 'tags':('family',),
                'job':{'name':'Killer','category':'Business'},
                'hobbies':[{'name':'counterstrike','period':1}]}
            ]

class AutoSet(object):
    def __init__(self, **kwargs):
        for name in kwargs:
            self.__setattr__(name, kwargs[name])

class Person(AutoSet):
    forename = ''
    surname = ''
    tags = ()
    age = 0
    job = None
    hobbies = []
    def __str__(self):
        return '<Person surname={0} forename={1} age={2} tags={3}>'.format(self.forename, self.surname,
                                                                          self.age, self.tags)

class Job(AutoSet):
    name = ''
    category = ''

class Hobby(AutoSet):
    name = ''
    period = 0

objectData = [
            Person(forename='Marc',surname='Mine',age=35, tags=('family','work'),
                   job=Job(name='Baker',category='Business'),
                   hobbies=[Hobby(name='swimming',period=7),
                            Hobby(name='reading',period=1)]
            ),
            Person(forename='Mike',surname='Meyer',age=14, tags=('work'),
                   job=Job(name='Banker',category='Business'),
                   hobbies=[Hobby(name='swimming',period=14)]
            ),
            Person(forename='Marc',surname='Andrew',age=78, tags=('hobby','work'),
                   job=Job(name='Police',category='Government'),
                   hobbies=[Hobby(name='swimming',period=7),
                            Hobby(name='music',period=1),
                            Hobby(name='reading',period=2),]
            ),
            Person(forename='Marc',surname='Muscels',age=35, tags=('family','hobby'),
                   job=Job(name='Teacher',category='Social'),
                   hobbies=[Hobby(name='math',period=30),
                            Hobby(name='ski',period=365)]
            ),
            Person(forename='Andy',surname='Young',age=11, tags=('family','work'),
                   job=Job(name='President',category='Government'),
                   hobbies=[Hobby(name='swimming',period=2),
                            Hobby(name='fitness',period=3),
                            Hobby(name='reading',period=4),
                            Hobby(name='rc-cars',period=14)]
            ),
            Person(forename='Andy',surname='Andy',age=51, tags=('family',),
                   job=Job(name='Killer',category='Business'),
                   hobbies=[Hobby(name='counterstrike',period=1)]
            )
            ]

if __name__ == '__main__':

    from sqliter.query import select, and_, or_, c, test

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