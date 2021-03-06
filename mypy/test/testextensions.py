import sys
import pickle
import typing
try:
    import collections.abc as collections_abc
except ImportError:
    import collections as collections_abc  # type: ignore # PY32 and earlier
from unittest import TestCase, main, skipUnless
sys.path[0:0] = ['extensions']
from mypy_extensions import TypedDict


class BaseTestCase(TestCase):

    def assertIsSubclass(self, cls, class_or_tuple, msg=None):
        if not issubclass(cls, class_or_tuple):
            message = '%r is not a subclass of %r' % (cls, class_or_tuple)
            if msg is not None:
                message += ' : %s' % msg
            raise self.failureException(message)

    def assertNotIsSubclass(self, cls, class_or_tuple, msg=None):
        if issubclass(cls, class_or_tuple):
            message = '%r is a subclass of %r' % (cls, class_or_tuple)
            if msg is not None:
                message += ' : %s' % msg
            raise self.failureException(message)


PY36 = sys.version_info[:2] >= (3, 6)

PY36_TESTS = """
Label = TypedDict('Label', [('label', str)])

class Point2D(TypedDict):
    x: int
    y: int

class LabelPoint2D(Point2D, Label): ...
"""

if PY36:
    exec(PY36_TESTS)


class TypedDictTests(BaseTestCase):

    def test_basics_iterable_syntax(self):
        Emp = TypedDict('Emp', {'name': str, 'id': int})
        self.assertIsSubclass(Emp, dict)
        self.assertIsSubclass(Emp, typing.MutableMapping)
        self.assertNotIsSubclass(Emp, collections_abc.Sequence)
        jim = Emp(name='Jim', id=1)
        self.assertIs(type(jim), dict)
        self.assertEqual(jim['name'], 'Jim')
        self.assertEqual(jim['id'], 1)
        self.assertEqual(Emp.__name__, 'Emp')
        self.assertEqual(Emp.__module__, 'mypy.test.testextensions')
        self.assertEqual(Emp.__bases__, (dict,))
        self.assertEqual(Emp.__annotations__, {'name': str, 'id': int})

    def test_basics_keywords_syntax(self):
        Emp = TypedDict('Emp', name=str, id=int)
        self.assertIsSubclass(Emp, dict)
        self.assertIsSubclass(Emp, typing.MutableMapping)
        self.assertNotIsSubclass(Emp, collections_abc.Sequence)
        jim = Emp(name='Jim', id=1)  # type: ignore # mypy doesn't support keyword syntax yet
        self.assertIs(type(jim), dict)
        self.assertEqual(jim['name'], 'Jim')
        self.assertEqual(jim['id'], 1)
        self.assertEqual(Emp.__name__, 'Emp')
        self.assertEqual(Emp.__module__, 'mypy.test.testextensions')
        self.assertEqual(Emp.__bases__, (dict,))
        self.assertEqual(Emp.__annotations__, {'name': str, 'id': int})

    def test_typeddict_errors(self):
        Emp = TypedDict('Emp', {'name': str, 'id': int})
        self.assertEqual(TypedDict.__module__, 'mypy_extensions')
        jim = Emp(name='Jim', id=1)
        with self.assertRaises(TypeError):
            isinstance({}, Emp)
        with self.assertRaises(TypeError):
            isinstance(jim, Emp)
        with self.assertRaises(TypeError):
            issubclass(dict, Emp)
        with self.assertRaises(TypeError):
            TypedDict('Hi', x=1)
        with self.assertRaises(TypeError):
            TypedDict('Hi', [('x', int), ('y', 1)])
        with self.assertRaises(TypeError):
            TypedDict('Hi', [('x', int)], y=int)

    @skipUnless(PY36, 'Python 3.6 required')
    def test_py36_class_syntax_usage(self):
        self.assertEqual(LabelPoint2D.__annotations__, {'x': int, 'y': int, 'label': str})  # noqa
        self.assertEqual(LabelPoint2D.__bases__, (dict,))  # noqa
        self.assertNotIsSubclass(LabelPoint2D, typing.Sequence)  # noqa
        not_origin = Point2D(x=0, y=1)  # noqa
        self.assertEqual(not_origin['x'], 0)
        self.assertEqual(not_origin['y'], 1)
        other = LabelPoint2D(x=0, y=1, label='hi')  # noqa
        self.assertEqual(other['label'], 'hi')

    def test_pickle(self):
        global EmpD  # pickle wants to reference the class by name
        EmpD = TypedDict('EmpD', name=str, id=int)
        jane = EmpD({'name': 'jane', 'id': 37})
        for proto in range(pickle.HIGHEST_PROTOCOL + 1):
            z = pickle.dumps(jane, proto)
            jane2 = pickle.loads(z)
            self.assertEqual(jane2, jane)
            self.assertEqual(jane2, {'name': 'jane', 'id': 37})
            ZZ = pickle.dumps(EmpD, proto)
            EmpDnew = pickle.loads(ZZ)
            self.assertEqual(EmpDnew({'name': 'jane', 'id': 37}), jane)


if __name__ == '__main__':
    main()
