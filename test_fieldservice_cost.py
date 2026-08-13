import unittest

from fieldservice_cost import WorkOrder, needs_human_review


class DispatchDecisionTest(unittest.TestCase):
    def test_urgent_visit_without_follow_up_stays_open_for_human_review(self):
        order = WorkOrder("WO-1042", "wet wall", "on site", "", "urgent")
        self.assertTrue(needs_human_review(order))

    def test_confirmed_routine_visit_can_close_after_note(self):
        order = WorkOrder("WO-1043", "intact seal", "complete", "replaced seal", "routine")
        self.assertFalse(needs_human_review(order))


if __name__ == "__main__":
    unittest.main()
