import requests
from datetime import datetime, timezone
# Special thanks to Copilot for making this
api_url = "https://api.modrinth.com/v2/search"

def fetch_projects(offset, q, order):  # facets are a bit finicky to customize so I just commented it out
    params = {
        "facets": '[["project_type:modpack"]]',     #["categories:fabric"] Change to apply filters, more info at https://docs.modrinth.com/api/operations/searchprojects/
        "query": q,
        "index": order,   # Sort by download count, recommended for this script
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

def calculate_score(project, order):
    #score = project["follows"]/project["downloads"] * 1000
    score = project[order] / ((datetime.now(timezone.utc) - datetime.fromisoformat(project["date_created"].replace("Z", "+00:00"))).total_seconds() / 86400.0)
    return score

def main():
    projectsFetched = ((int(input("Enter number of projects to be fetched (will be rounded up to nearest hundred): ")) // 100) + 1) * 100    # rounds up to nearest hundred due to the limit
    rankNum = int(input("Enter the number of top projects to display: "))
    order = str(input("Sort by 'follows' or 'downloads':")).strip()
    if order!= "follows" and order != "downloads":
        print("Invalid sort order. Defaulting to 'downloads'.")
        order = "downloads"
    print("Edit program (Line 8) to apply filters,")
    query = str(input("Enter a search query (leave empty for all projects): ")).strip()
    if not query:
        query = ""
    pagination = 0
    all_projects = []
    while pagination < projectsFetched:
        print(f"Fetching projects: {pagination} / {projectsFetched}")
        projects = fetch_projects(pagination, query, order)
        if not projects:    # If no projects are returned, break the loop
            print("No more projects found or an error occurred.")
            break
        all_projects.extend(projects)
        pagination += 100
    for project in all_projects:
        project["current_score"] = calculate_score(project, order)
    print(f"Fetched {len(all_projects)} projects.")
    all_projects.sort(key=lambda project: project["current_score"], reverse=True)
    print("\n{:>4} {:<50} {:>12} {:>12} {:>10}".format("Rank", "Title", order.capitalize(), "/Day", "Δ%"))
    print("-" * 100)
    previous_score = None
    for i, project in enumerate(all_projects[:rankNum], start=1):
        if previous_score is None:
            perc_diff = ""
        else:
            perc_diff = f"{((project['current_score'] / previous_score - 1) * 100):+7.1f}%"
        print("{:>4} {:<50} {:>12} {:>12.1f} {:>10}".format(
            i,
            project["title"][:47] + "..." if len(project["title"]) > 50 else project["title"],
            project[order],
            project["current_score"],
            perc_diff
        ))
        previous_score = project["current_score"]

if __name__ == "__main__":
    main()