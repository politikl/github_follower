#!/usr/bin/env python3
"""GitHub Follow Manager - Sync your followers and following."""

import requests

# ============ CONFIGURATION ============
GITHUB_TOKEN = ""  # Paste your GitHub token here
NEVER_UNFOLLOW = set()  # Users to never unfollow (case-sensitive usernames)
# =======================================

API_BASE = "https://api.github.com"


def get_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def get_username():
    resp = requests.get(f"{API_BASE}/user", headers=get_headers())
    resp.raise_for_status()
    return resp.json()["login"]


def get_all_paginated(url):
    users = []
    while url:
        resp = requests.get(url, headers=get_headers(), params={"per_page": 100})
        resp.raise_for_status()
        users.extend(user["login"] for user in resp.json())
        url = resp.links.get("next", {}).get("url")
    return set(users)


def get_followers(username):
    return get_all_paginated(f"{API_BASE}/users/{username}/followers")


def get_following(username):
    return get_all_paginated(f"{API_BASE}/users/{username}/following")


def follow_user(username):
    resp = requests.put(f"{API_BASE}/user/following/{username}", headers=get_headers())
    return resp.status_code == 204


def unfollow_user(username):
    resp = requests.delete(f"{API_BASE}/user/following/{username}", headers=get_headers())
    return resp.status_code == 204


def main():
    if not GITHUB_TOKEN:
        print("Error: Please set your GITHUB_TOKEN in the script.")
        return

    print("Fetching your GitHub info...")
    username = get_username()
    print(f"Logged in as: {username}\n")

    followers = get_followers(username)
    following = get_following(username)

    print(f"Followers: {len(followers)}")
    print(f"Following: {len(following)}\n")

    # People who follow you but you don't follow back
    to_follow = followers - following
    # People you follow but don't follow you back
    to_unfollow = following - followers

    print(f"Users to follow back: {len(to_follow)}")
    print(f"Users to unfollow: {len(to_unfollow)}\n")

    if to_follow:
        print("Following back...")
        for user in to_follow:
            if follow_user(user):
                print(f"  ✓ Followed {user}")
            else:
                print(f"  ✗ Failed to follow {user}")

    if to_unfollow:
        print("\nUnfollowing non-followers...")
        for user in to_unfollow:
            if user in NEVER_UNFOLLOW:
                print(f"  ⊘ Skipped {user} (protected)")
                continue
            if unfollow_user(user):
                print(f"  ✓ Unfollowed {user}")
            else:
                print(f"  ✗ Failed to unfollow {user}")

    print("\nDone!")


if __name__ == "__main__":
    main()
