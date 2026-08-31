import requests
from datetime import datetime


LEETCODE_URL = "https://leetcode.com/graphql"


def get_recent_accepted_submissions(username, limit=20):
    query = """
    query recentAcSubmissions($username: String!, $limit: Int!) {
        recentAcSubmissionList(username: $username, limit: $limit) {
            id
            title
            titleSlug
            timestamp
        }
    }
    """

    response = requests.post(
        LEETCODE_URL,
        json={
            "query": query,
            "variables": {
                "username": username,
                "limit": limit,
            },
        },
        timeout=10,
    )

    response.raise_for_status()

    data = response.json()

    return data["data"]["recentAcSubmissionList"]

def todays_submissions(username):
    submissions = get_recent_accepted_submissions(username)

    today = datetime.now().date()

    results = []

    for submission in submissions:
        submission_date = datetime.fromtimestamp(
            int(submission["timestamp"])
        ).date()

        if submission_date == today:
            results.append(submission)

    return results

def solved_today(username):
    return len(todays_submissions(username)) > 0