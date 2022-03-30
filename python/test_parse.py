import unittest
from parameterized import parameterized
from main import ToggleEngine
import json


class TestStringMethods(unittest.TestCase):
    # @parameterized.expand(
    #     [
    #         [
    #             {
    #                 "name": "Feature.D2",
    #                 "enabled": True,
    #                 "strategies": [
    #                     {
    #                         "name": "userWithId",
    #                         "parameters": {"userIds": "123, 222, 88"},
    #                     }
    #                 ],
    #             },
    #             {"userId": "222"},
    #             True,
    #         ]
    #     ]
    # )
    # def test_parses_specific(self, toggle, context, expected):

    #     toggle_engine = ToggleEngine()
    #     toggle_engine.update([toggle])
    #     enabled = toggle_engine.is_enabled(toggle["name"], context)
    #     print(enabled, expected)
    #     assert enabled == expected

    @parameterized.expand(
        [
            ["01-simple-examples.json"],
            ["02-user-with-id-strategy.json"],
            # ["03-gradual-rollout-user-id-strategy.json"]
        ]
    )
    def test_spec(self, filename):
        root_folder = "client_specifications/specifications"
        with open(f"{root_folder}/{filename}") as _file:
            test_data = json.loads(_file.read())
            test_name = test_data["name"]

            features = test_data["state"]["features"]
            test_cases = test_data["tests"]
            print(f"Running test: {test_name}")

            toggle_engine = ToggleEngine()
            toggle_engine.update(features)

            for test_case in test_cases:
                print("Running case:", test_case["description"])
                expected_result = test_case["expectedResult"]
                toggle_name = test_case["toggleName"]
                context = test_case["context"]
                enabled = toggle_engine.is_enabled(toggle_name, context)
                print("Actual", enabled, "expected", expected_result)
                assert(enabled == expected_result)


if __name__ == "__main__":
    unittest.main()
