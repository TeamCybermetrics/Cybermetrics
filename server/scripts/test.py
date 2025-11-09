from pybaseball import playerid_lookup

# df = playerid_lookup("Betts", "Mookie")
# print(df.columns)
# print(df.T)


from pybaseball import fielding_stats

fs = fielding_stats(2023)
print(fs[['Name', 'Pos']].head())
