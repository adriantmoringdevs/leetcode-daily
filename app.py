from leetcode import todays_submissions


username = input("Enter your LeetCode username: ")

submissions = todays_submissions(username)

print("\nToday's submissions:")

for submission in submissions:
    print(
        submission["title"],
        submission["timestamp"]
    )