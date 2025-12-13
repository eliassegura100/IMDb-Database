from imdb_dal import (
    search_titles_by_name,
    get_title_by_id,
    get_filmography_for_person,
    insert_title,
    update_title,
    get_top_titles_by_genre,
    get_top_costars,
    delete_title_and_relationships,
)

def prompt_int(message, allow_blank=False):
    s = input(message).strip()
    if allow_blank and s == "":
        return None
    try:
        return int(s)
    except ValueError:
        print("Please enter a valid integer.")
        return prompt_int(message, allow_blank)
    
def prompt_str(message, allow_blank=False):
    s = input(message).strip()
    if not allow_blank and s == "":
        print("Input cannot be blank.")
        return prompt_str(message, allow_blank=allow_blank)
    return s

def print_title_row(t):
    year = t.get("startYear")
    print(f'{t.get("tconst")} "{t.get("primaryTitle")}" ({year})')

def menu():
    print("\nIMDb Application Menu")
    print("1. Search Titles by Name")
    print("2. Get Title by ID")
    print("3. Get Filmography for Person")
    print("4. Insert New Title")
    print("5. Update Existing Title")
    print("6. Delete Title and Relationships")
    print("7. Get Top Titles by Genre")
    print("8. Get Top Co-stars for Person")
    print("0. Exit")

def run():
    while True:
        menu()
        choice = input("\nSelect an option: ").strip()

        if choice == "0":
            print("Exiting IMDb Application.")
            return
        elif choice == "1":
            title_query = prompt_str("Title search query: ")
            limit = prompt_int("Limit (default 25): ", allow_blank=True) or 25
            results = search_titles_by_name(title_query, limit)
            if not results:
                print("No titles found.")
            else:
                for t in results:
                    print_title_row(t)
        elif choice == "2":
            tconst = prompt_str("Enter tconst (e.g. tt0133093 or UUID):")
            t = get_title_by_id(tconst)
            if not t:
                print(f"No title found with tconst {tconst}.")
            else:
                print("\nTitle details:")
                for k, v in t.items():
                    print(f"  {k}: {v}")
        elif choice == "3":
            person_name = prompt_str("Person name query: ")
            results = get_filmography_for_person(person_name)
            if not results:
                print("No filmography found.")
            else:
                for record in results:
                    person = record["person"]
                    title = record["title"]
                    year = record["year"]

                    category = record.get("category", "unknown")
                    ordering = record.get("ordering")

                    print(
                        f'{person} '
                        f'({category}, cast list #{ordering}) '
                        f'-> {title} ({year})'
                    )
        elif choice == "4":
            title = prompt_str("New title name: ")
            year = prompt_int("Start year (leave blank if unknown): ", allow_blank=True)
            title_type = prompt_str('Title type (default "movie"): ', allow_blank=True) or "movie"
            runtime = prompt_int("Runtime minutes (blank for none): ", allow_blank=True)

            created = insert_title(
                primary_title=title,
                start_year=year,
                title_type=title_type,
                runtime_minutes=runtime
            )
            print("\nCreated:")
            print(created)

        elif choice == "5":
            tconst = prompt_str("tconst to update: ")
            print("Leave fields blank to keep existing values.\n")
            new_title = prompt_str("New primaryTitle: ", allow_blank=True)
            new_year = prompt_int("New startYear: ", allow_blank=True)
            new_type = prompt_str("New titleType: ", allow_blank=True)
            new_runtime = prompt_int("New runtimeMinutes: ", allow_blank=True)

            updated = update_title(
                tconst=tconst,
                primary_title=new_title,
                start_year=new_year,
                title_type=new_type,
                runtime_minutes=new_runtime
            )
            if not updated:
                print("No title found for that ID.")
            else:
                print("\nUpdated:")
                print(updated)

        elif choice == "6":
            tconst = prompt_str("tconst to delete: ")
            confirm = prompt_str(f'Type DELETE to confirm deleting "{tconst}": ')
            if confirm != "DELETE":
                print("Cancelled.")
            else:
                deleted = delete_title_and_relationships(tconst)
                if deleted == 1:
                    print("Deleted successfully.")
                else:
                    print("No title found; nothing deleted.")

        elif choice == "7":
            genre = prompt_str("Genre name (exact, e.g. Drama): ")
            start_year = prompt_int("Start year (blank for none): ", allow_blank=True)
            end_year = prompt_int("End year (blank for none): ", allow_blank=True)
            limit = prompt_int("Limit (default 20): ", allow_blank=True) or 20

            rows = get_top_titles_by_genre(genre, start_year=start_year, end_year=end_year, limit=limit)
            if not rows:
                print("No results (check genre spelling or year range).")
            else:
                for r in rows:
                    print(f'{r["tconst"]}  "{r["primaryTitle"]}" ({r["startYear"]})  rating={r["averageRating"]} votes={r["numVotes"]}')

        elif choice == "8":
            name_q = prompt_str("Person name query: ")
            min_shared = prompt_int("Minimum shared titles (default 2): ", allow_blank=True) or 2
            limit = prompt_int("Limit (default 20): ", allow_blank=True) or 20

            rows = get_top_costars(name_q, min_shared_credits=min_shared, limit=limit)
            if not rows:
                print("No results (try a different person name).")
            else:
                main = rows[0]["mainPerson"]
                print(f"\nTop co-stars for: {main}\n")
                for r in rows:
                    print(f'{r["costar"]}: {r["sharedTitles"]} shared title(s)')

        else:
            print("Invalid option. Please choose 0-7.")

if __name__ == "__main__":
    run()
