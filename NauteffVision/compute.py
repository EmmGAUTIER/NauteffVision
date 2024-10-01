###############################################################################
#
# This file is part of the Nauteff Autopilot project.
#
# Copyright (C) 2023 Nauteff https://nauteff.com
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import os
import queue
import selectors
import threading
import time
import data


class DataProcess(data.DataInterface):
    def __init__(self, config, queue_out):
        super().__init__(config, queue_out)

    def put_data(self, data):
        res = 0
        if self.direction == "out":
            res = self.file_out.write(data.str4log() + '\n')
            self.file_out.flush()
        return res

    def get_data_list_in(self) -> list:
        # do not listen
        return []

    def get_data_list_out(self) -> list:
        return ["all"]

    def run(self):
        return

    def terminate(self):
        pass
