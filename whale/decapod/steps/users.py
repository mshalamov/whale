"""
----------
User steps
----------
"""

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from hamcrest import (assert_that,equal_to, has_entries)  # noqa
from decapodlib import exceptions

from stepler.base import BaseSteps
from stepler.third_party import steps_checker
from stepler.third_party import waiter

__all__ = [
    'UserSteps'
]


class UserSteps(BaseSteps):
    """User steps."""

    @steps_checker.step
    def create_user(self,
                    user_name,
                    full_name,
                    email,
                    role_id=None,
                    check=True,
                    **kwargs):
        """Step to create new user.

        Args:
            user_name (str): the new name of the user
            full_name (str): the new full name of the user
            email (str): the new email of the user
            role_id (str): the new role id of the user
            check (bool): flag whether to check step or not
            **kwargs: any other attribute provided will be passed to server

        Returns:
            json: model of new user

        Raises:
            TimeoutExpired|AssertionError: if check was triggered to an error
        """
        user = self._client.create_user(login=user_name,
                                        full_name=full_name,
                                        email=email,
                                        role_id=role_id,
                                        **kwargs)

        if check:
            self.check_user_presence(user.get('id'))
            assert_that(user['data']['login'], equal_to(user_name))

            if full_name:
                assert_that(user['data']['full_name'],
                            equal_to(full_name))
            if email:
                assert_that(user['data']['email'], equal_to(email))
            if role_id:
                assert_that(user["data"]["role_id"],
                            equal_to(role_id))

        return user

    @steps_checker.step
    def delete_user(self, user_id, check=True, **kwargs):
        """Step to delete user.

        Args:
            user_id (str): user id
            check (bool): flag whether to check step or not
            **kwargs: any other attribute provided will be passed to server
        """
        self._client.delete_user(user_id, **kwargs)
        if check:
            self.check_user_presence(user_id, must_present=False)

    @steps_checker.step
    def check_user_presence(self, user_id, must_present=True, timeout=0):
        """Step to check user presence.

        Args:
            user_id (str): user id
            must_present (bool): flag whether user should present or not
            timeout (int): seconds to wait a result of check

        Raises:
            TimeoutExpired: if check failed after timeout
        """
        def _check_user_presence():
            try:
                user = self._client.get_user(user_id)
                if user['time_deleted'] == 0:
                    is_present = True
                if user['time_deleted'] != 0:
                    is_present = False
            except exceptions.DecapodAPIError:
                is_present = False

            return waiter.expect_that(is_present, equal_to(must_present))

        waiter.wait(_check_user_presence, timeout_seconds=timeout)
