import unittest

import grakn

import kgcn.src.neighbourhood.schema.executor as ex
import kgcn.src.neighbourhood.schema.strategy as strat
import kgcn.src.neighbourhood.schema.traversal as trv


class TestGetSchemaConceptTypes(unittest.TestCase):

    def setUp(self):
        client = grakn.Grakn(uri="localhost:48555")
        session = client.session(keyspace="test_schema")
        self._tx = session.transaction(grakn.TxType.WRITE)

    def tearDown(self):
        self._tx.close()

    def _function_calls(self, query, include_implicit, include_metatypes):
        exec = ex.TraversalExecutor(self._tx)
        schema_concept_types = exec.get_schema_concept_types(query, include_implicit=include_implicit, include_metatypes=include_metatypes)
        labels = trv.labels_from_types(schema_concept_types)
        return labels

    def _filtering(self, query, num_types):
        with self.subTest('implicit_filtering'):
            labels = self._function_calls(query, False, True)
            # Make sure none of the type labels contain '@has-' which indicates that the type is implicit
            self.assertFalse(any(['@has-' in label for label in labels]))

        with self.subTest('metatype_filtering'):
            labels = self._function_calls(query, True, False)
            self.assertFalse(any([label in trv.METATYPE_LABELS for label in labels]))

        with self.subTest('all_members'):
            labels = list(self._function_calls(query, True, True))
            print(labels)

            with self.subTest("contains implicit"):
                self.assertTrue(any([label in trv.METATYPE_LABELS for label in labels]))

            with self.subTest("contains metatypes"):
                self.assertFalse(all([label in trv.METATYPE_LABELS for label in labels]))

            with self.subTest("length correct"):
                self.assertEqual(len(labels), num_types)

    def test_thing_filtering(self):
        self._filtering(strat.GET_THING_TYPES_QUERY, 16)

    def test_role_filtering(self):
        self._filtering(strat.GET_ROLE_TYPES_QUERY, 14)

    def test_integration(self):
        client = grakn.Grakn(uri="localhost:48555")
        session = client.session(keyspace="test_schema")
        tx = session.transaction(grakn.TxType.WRITE)

        print("================= THINGS ======================")
        te = ex.TraversalExecutor(tx)
        schema_concept_types = te.get_schema_concept_types(strat.GET_THING_TYPES_QUERY, include_implicit=True,
                                                           include_metatypes=False)
        labels = trv.labels_from_types(schema_concept_types)
        print(list(labels))

        schema_concept_types = te.get_schema_concept_types(strat.GET_THING_TYPES_QUERY, include_implicit=True,
                                                           include_metatypes=False)
        super_types = trv.get_sups_labels_per_type(schema_concept_types, include_self=True, include_metatypes=False)
        print("==== super types ====")
        [print(type, super_types) for type, super_types in super_types.items()]

        print("================= ROLES ======================")
        schema_concept_types = te.get_schema_concept_types(strat.GET_ROLE_TYPES_QUERY, include_implicit=True,
                                                           include_metatypes=False)
        labels = trv.labels_from_types(schema_concept_types)
        print(list(labels))

        schema_concept_types = te.get_schema_concept_types(strat.GET_ROLE_TYPES_QUERY, include_implicit=True,
                                                           include_metatypes=False)
        super_types = trv.get_sups_labels_per_type(schema_concept_types, include_self=True, include_metatypes=False)
        print("==== super types ====")
        [print(type, super_types) for type, super_types in super_types.items()]