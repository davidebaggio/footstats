from scraper import *

if __name__ == '__main__':
	with open("campionato.json", "r") as file:
		campionato = json.load(file)
	with open("campionato.old", "w") as file:
		json.dump(campionato, file, indent=4)
	print("1. Add match\n2. Display leaderboard")
	choice = input("(1/2): ")
	if choice == "1":
		add_match(campionato)
	elif choice == "2":
		display_leaderboard(campionato)
	else:
		print("Invalid choice")