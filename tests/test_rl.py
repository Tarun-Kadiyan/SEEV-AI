import importlib.util
import random
import sqlite3
import tempfile
import unittest
from pathlib import Path

SPEC=importlib.util.spec_from_file_location('rl_under_test',Path(__file__).resolve().parents[1]/'rl_engine.py')
rl=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rl)

class BanditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.original=rl.DB_PATH
        rl.DB_PATH=Path(self.tmp.name)/'test.db'
        rl.init_rl_db()
        with sqlite3.connect(rl.DB_PATH) as con:
            con.execute('CREATE TABLE analyses (id INTEGER PRIMARY KEY, user_id INTEGER, mode TEXT)')
            con.executemany('INSERT INTO analyses VALUES (?,?,?)',[(i,1,'Individual') for i in [101,200,201,202,203,300,401,402]])
            con.execute('INSERT INTO analyses VALUES (501,1,"Company")')
            con.execute('INSERT INTO analyses VALUES (502,1,"Company")')
        self.result={'score':45,'missing_skills':['python','sql']}
    def tearDown(self):
        rl.DB_PATH=self.original
        self.tmp.cleanup()
    def test_persistent_action_and_single_reward(self):
        a=rl.get_or_create_recommendation(1,101,self.result,rng=random.Random(1))
        b=rl.get_or_create_recommendation(1,101,self.result,rng=random.Random(2))
        self.assertEqual(a['id'],b['id'])
        self.assertTrue(rl.record_reward(1,a['id'],'Yes'))
        self.assertFalse(rl.record_reward(1,a['id'],'No'))
        self.assertEqual(rl.learning_summary(1)['rated'],1)
        self.assertEqual(rl.learning_summary(2)['rated'],0)
    def test_cold_start_explores_all_actions(self):
        actions=set()
        for i in range(4):
            decision=rl.get_or_create_recommendation(1,200+i,self.result,rng=random.Random(i))
            actions.add(decision['action'])
            self.assertEqual(decision['strategy'],'cold_start')
            rl.record_reward(1,decision['id'],'Yes' if decision['action']=='projects' else 'No')
        self.assertEqual(actions,set(rl.ACTIONS))
        # With epsilon=0, always exploit the highest mean reward after cold start.
        decision=rl.get_or_create_recommendation(1,300,self.result,rng=random.Random(42),epsilon=0)
        self.assertEqual(decision['action'],'projects')
        self.assertEqual(decision['strategy'],'exploit')
    def test_context_and_user_isolation(self):
        rl.get_or_create_recommendation(1,401,self.result,rng=random.Random(0))
        stats=rl.action_stats(2,rl.context_for(self.result))
        self.assertTrue(all(s['count']==0 for s in stats.values()))
        no_gaps={'score':90,'missing_skills':[]}
        self.assertNotIn('technical_skills',rl.eligible_actions(no_gaps))
        self.assertNotEqual(rl.context_for(no_gaps),rl.context_for(self.result))
    def test_company_mode_feedback_isolated(self):
        d=rl.get_or_create_recommendation(1,501,self.result,mode='Company',rng=random.Random(1))
        self.assertIn(d['action'],rl.COMPANY_ACTIONS)
        self.assertTrue(rl.record_reward(1,d['id'],'Yes'))
        self.assertEqual(rl.learning_summary(1,'Company')['rated'],1)
        self.assertEqual(rl.learning_summary(1,'Individual')['rated'],0)
        d2=rl.get_or_create_recommendation(1,502,self.result,mode='Company',rng=random.Random(2))
        self.assertIn(d2['action'],rl.COMPANY_ACTIONS)
        with self.assertRaises(ValueError):
            rl.get_or_create_recommendation(1,101,self.result,mode='Company')
    def test_invalid_rating(self):
        d=rl.get_or_create_recommendation(1,402,self.result)
        with self.assertRaises(ValueError):rl.record_reward(1,d['id'],'maybe')

if __name__=='__main__':unittest.main()
