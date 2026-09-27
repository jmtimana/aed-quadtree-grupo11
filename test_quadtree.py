import random
import unittest
from quadtree import QuadTree, Point, example, EXTRA

class Tests(unittest.TestCase):
    def test_random_against_set(self):
        rng=random.Random(2026); q=QuadTree(bits=4,trace=False); expected=set()
        for _ in range(500):
            p=Point(rng.randrange(16),rng.randrange(16))
            xy=(p.x,p.y)
            if rng.random()<.6:
                self.assertEqual(q.insert(p),xy not in expected); expected.add(xy)
            else:
                self.assertEqual(q.delete(p),xy in expected); expected.discard(xy)
            self.assertEqual({(p.x,p.y) for p in q.traverse()},expected)
            def invariant(n):
                if n.children:
                    self.assertEqual(len(n.children),4); self.assertIsNone(n.point)
                    for c in n.children: invariant(c)
                elif n.point:
                    self.assertTrue(n.x<=n.point.x<n.x+n.side)
                    self.assertTrue(n.y<=n.point.y<n.y+n.side)
            invariant(q.root)
    def test_worst_and_merge(self):
        q=QuadTree(); a=Point(0,0,'P'); b=Point(1,1,'Q')
        q.insert(a); q.insert(b)
        self.assertEqual(q.stats(),(33,8))
        self.assertEqual(sum(e['kind']=='split' for e in q.events),8)
        self.assertTrue(q.delete(b))
        self.assertEqual(sum(e['kind']=='merge' for e in q.events),8)
        self.assertEqual(q.stats(),(1,0))
    def test_boundaries_and_order(self):
        q=QuadTree(); self.assertEqual(q.traverse(),[])
        self.assertFalse(q.insert(Point(256,0)))
        self.assertTrue(q.insert(Point(128,128,'M')))
        self.assertFalse(q.insert(Point(128,128,'X')))
        self.assertFalse(q.delete(Point(1,2)))
        q=example(True)
        self.assertEqual([p.name for p in q.traverse()],['A','E','B','C','D'])
        q.delete(EXTRA); self.assertEqual(q.stats(),(5,1))

if __name__=='__main__': unittest.main()
