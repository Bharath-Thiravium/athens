from rest_framework import status


def assert_401(testcase, response):
    testcase.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


def assert_403_or_404(testcase, response):
    testcase.assertIn(response.status_code, {status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND})
