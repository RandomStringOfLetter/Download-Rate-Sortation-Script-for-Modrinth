import requests
from datetime import datetime, timezone
# Special thanks to Copilot for making this
api_url = "https://api.modrinth.com/v2/search"

def fetch_projects(offset, q):  # facets are a bit finicky to customize so I just commented it out
    params = {
    #    "facets": '[["categories:fabric"], ["project_type:datapack"]]',    # Change to apply filters, more info at https://docs.modrinth.com/api/operations/searchprojects/
        "query": q,
        "index": "downloads",   # Sort by download count, recommended for this script
        "limit": 100,           # fetch 100 projects at a time
        "offset": offset,
    }
    try:
        response = requests.get(api_url, params)
        response.raise_for_status()
        return response.json().get("hits", [])
    except (requests.RequestException, ValueError) as e:    # Handle network or JSON parsing errors
        print(f"Error fetching projects: {e}")
        return []

def calculate_score(project):
    return project["downloads"] / ((datetime.now(timezone.utc) - datetime.fromisoformat(project["date_created"].replace("Z", "+00:00"))).total_seconds() / 86400.0)

def main():
    projectsFetched = ((int(input("Enter number of projects to be fetched (will be rounded up to nearest hundred): ")) // 100) + 1) * 100    # rounds up to nearest hundred due to the limit
    rankNum = int(input("Enter the number of top projects to display: "))
    print("Edit program (Line 8) to apply filters,")
    query = str(input("Enter a search query (leave empty for all projects): ")).strip()
    if not query:
        query = ""
    pagination = 0
    all_projects = []
    while pagination < projectsFetched:
        print(f"Fetching projects: {pagination} / {projectsFetched}")
        projects = fetch_projects(pagination, query)
        if not projects:    # If no projects are returned, break the loop
            print("No more projects found or an error occurred.")
            break
        all_projects.extend(projects)
        pagination += 100
    print(f"Fetched {len(all_projects)} projects.")
    all_projects.sort(key=calculate_score, reverse=True)
    print("\n{:>4} {:<50} {:>12} {:>12}".format("Rank", "Title", "Downloads", "/Day"))
    print("-" * 80)
    for i, project in enumerate(all_projects[:rankNum], start=1):
        print("{:>4} {:<50} {:>12} {:>12.1f}".format(   # Emojis fuck with the formatting fsr
        i,
        project["title"][:47] + "..." if len(project["title"]) > 50 else project["title"],
        project["downloads"],
        calculate_score(project)
    ))

if __name__ == "__main__":
    main()