# Copyright 2013-2021 Aerospike, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from lib.base_controller import ShellException
import unittest
from mock import patch

from lib.live_cluster.show_controller import (
    ShowStatisticsController,
    ShowUsersController,
)
from lib.live_cluster.live_cluster_root_controller import LiveClusterRootController
from lib.live_cluster.client.info import ASProtocolError, ASResponse
from test.unit import util as test_util


@patch("lib.base_controller.BaseController.view")
class ShowStatisticsControllerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.cluster_mock = patch(
            "lib.live_cluster.live_cluster_root_controller.Cluster"
        ).start()
        self.root_controller = LiveClusterRootController()
        self.controller = ShowStatisticsController()
        self.controller.mods = (
            {}
        )  # For some reason they are being polluted from other tests
        self.getter_mock = patch(
            "lib.live_cluster.show_controller.GetStatisticsController"
        ).start()
        self.controller.getter = self.getter_mock
        self.mods = {}

        self.addCleanup(patch.stopall)

    def test_do_service_default(self, view_mock):
        line = ["service"]
        mods = {"like": [], "with": [], "for": [], "line": []}
        stats = {"service": "stats"}
        self.getter_mock.get_service.return_value = stats

        # self.controller.pre_command(line[:])
        self.controller.execute(line)

        self.getter_mock.get_service.assert_called_with(nodes="all")
        view_mock.show_stats.assert_called_with(
            "Service Statistics",
            stats,
            self.root_controller.cluster,
            show_total=False,
            title_every_nth=0,
            flip_output=False,
            **mods,
        )

    def test_do_service_modifiers(self, view_mock):
        line = ["service", "with", "1.2.3.4", "like", "foo", "for", "bar"]
        mods = {"like": ["foo"], "with": ["1.2.3.4"], "for": ["bar"], "line": []}
        stats = {"service": "stats"}
        self.getter_mock.get_service.return_value = stats

        self.controller.execute(line)

        self.getter_mock.get_service.assert_called_with(nodes=["1.2.3.4"])
        view_mock.show_stats.assert_called_with(
            "Service Statistics",
            stats,
            self.root_controller.cluster,
            show_total=False,
            title_every_nth=0,
            flip_output=False,
            **mods,
        )

    def test_do_service_args(self, view_mock):
        line = ["service", "-t", "-r", "17", "-flip"]
        mods = {"like": [], "with": [], "for": [], "line": line[1:]}
        stats = {"service": "stats"}
        self.getter_mock.get_service.return_value = stats

        self.controller.execute(line)

        self.getter_mock.get_service.assert_called_with(nodes="all")
        view_mock.show_stats.assert_called_with(
            "Service Statistics",
            stats,
            self.root_controller.cluster,
            show_total=True,
            title_every_nth=17,
            flip_output=True,
            **mods,
        )

    def test_do_sindex(self, view_mock):
        node_addr = "1.2.3.4"
        like = "foo"
        for_ = "bar"
        line = [
            "sindex",
            "with",
            node_addr,
            "like",
            like,
            "for",
            for_,
            "-t",
            "-r",
            "17",
            "-flip",
        ]
        mods = {"like": [like], "with": [node_addr], "for": [for_], "line": []}
        stats = {"sindex1": "stats1", "sindex2": "stats2", "sindex3": "stats3"}
        self.getter_mock.get_sindex.return_value = stats

        self.controller.execute(line)

        self.getter_mock.get_sindex.assert_called_with(
            nodes=[node_addr], for_mods=[for_]
        )
        self.assertEqual(view_mock.show_stats.call_count, 3)

        print(self.controller.mods)

        for ns_set_sindex in stats:
            view_mock.show_stats.assert_any_call(
                "{} Sindex Statistics".format(ns_set_sindex),
                stats[ns_set_sindex],
                self.root_controller.cluster,
                show_total=True,
                title_every_nth=17,
                flip_output=True,
                **mods,
            )

    def test_do_sets(self, view_mock):
        node_addr = "1.2.3.4"
        like = "foo"
        for_ = "bar"
        line = [
            "sets",
            "with",
            node_addr,
            "like",
            like,
            "for",
            for_,
            "-t",
            "-r",
            "17",
            "-flip",
        ]
        mods = {"like": [like], "with": [node_addr], "for": [for_], "line": []}
        stats = {
            ("ns1", "set1"): "stats1",
            ("ns2", "set2"): "stats2",
            ("ns3", "set3"): "stats3",
        }
        self.getter_mock.get_sets.return_value = stats

        self.controller.execute(line)

        self.getter_mock.get_sets.assert_called_with(nodes=[node_addr], for_mods=[for_])
        self.assertEqual(view_mock.show_stats.call_count, 3)

        for namespace, set_ in stats:
            view_mock.show_stats.assert_any_call(
                "{} {} Set Statistics".format(namespace, set_),
                stats[(namespace, set_)],
                self.root_controller.cluster,
                show_total=True,
                title_every_nth=17,
                flip_output=True,
                **mods,
            )

    def test_do_bins(self, view_mock):
        node_addr = "1.2.3.4"
        like = "foo"
        for_ = "bar"
        line = [
            "bins",
            "with",
            node_addr,
            "like",
            like,
            "for",
            for_,
            "-t",
            "-r",
            "17",
            "-flip",
        ]
        mods = {"like": [like], "with": [node_addr], "for": [for_], "line": []}
        stats = {
            "ns1": "stats1",
            "ns2": "stats2",
            "ns3": "stats3",
        }
        self.getter_mock.get_bins.return_value = stats

        self.controller.execute(line)

        self.getter_mock.get_bins.assert_called_with(nodes=[node_addr], for_mods=[for_])
        self.assertEqual(view_mock.show_stats.call_count, 3)

        for namespace in stats:
            view_mock.show_stats.assert_any_call(
                "{} Bin Statistics".format(namespace),
                stats[namespace],
                self.root_controller.cluster,
                show_total=True,
                title_every_nth=17,
                flip_output=True,
                **mods,
            )


class ShowUsersControllerTest(unittest.TestCase):
    def setUp(self) -> None:
        patch("lib.live_cluster.live_cluster_root_controller.Cluster").start()
        self.root_controller = LiveClusterRootController()
        self.controller = ShowUsersController()
        self.cluster_mock = patch(
            "lib.live_cluster.show_controller.ShowUsersController.cluster"
        ).start()
        self.getter_mock = patch(
            "lib.live_cluster.show_controller.GetUsersController"
        ).start()
        self.view_mock = patch(
            "lib.base_controller.BaseController.view.show_users"
        ).start()
        self.logger_mock = patch("lib.base_controller.BaseController.logger").start()
        self.controller.getter = self.getter_mock
        self.controller.mods = {}

        self.addCleanup(patch.stopall)

    def test_success(self):
        resp = {
            "admin": {
                "roles": ["user-admin"],
                "read-info": {
                    "quota": 0,
                    "single-record-tps": 0,
                    "scan-query-rps-limited": 0,
                    "scan-query-limitless": 0,
                },
                "write-info": {
                    "quota": 0,
                    "single-record-tps": 0,
                    "scan-query-rps-limited": 0,
                    "scan-query-limitless": 0,
                },
                "connections": 4294966442,
            },
            "alpha-reader": {
                "roles": ["alpha-reader"],
                "read-info": {
                    "quota": 0,
                    "single-record-tps": 0,
                    "scan-query-rps-limited": 0,
                    "scan-query-limitless": 0,
                },
                "write-info": {
                    "quota": 0,
                    "single-record-tps": 0,
                    "scan-query-rps-limited": 0,
                    "scan-query-limitless": 0,
                },
            },
        }
        self.cluster_mock.get_expected_principal.return_value = "test-principal"
        self.getter_mock.get_users.return_value = {"1.1.1.1": resp}

        self.controller.execute(["like", "admin"])

        self.getter_mock.get_users.assert_called_with(nodes=["test-principal"])
        self.view_mock.assert_called_with(resp, like=["admin"], line=[])

    def test_logs_error(self):
        as_error = ASProtocolError(
            ASResponse.ROLE_OR_PRIVILEGE_VIOLATION, "test-message"
        )
        self.cluster_mock.get_expected_principal.return_value = "test-principal"
        self.getter_mock.get_users.return_value = {"1.1.1.1": as_error}

        self.controller.execute(["like", "admin"])

        self.getter_mock.get_users.assert_called_with(nodes=["test-principal"])
        self.logger_mock.error.assert_called_with(as_error)
        self.view_mock.assert_not_called()

    def test_raises_error(self):
        as_error = IOError("test-message")
        self.cluster_mock.get_expected_principal.return_value = "test-principal"
        self.getter_mock.get_users.return_value = {"1.1.1.1": as_error}

        test_util.assert_exception(
            self,
            ShellException,
            "test-message",
            self.controller.execute,
            ["like", "admin"],
        )

        self.getter_mock.get_users.assert_called_with(nodes=["test-principal"])
        self.view_mock.assert_not_called()

