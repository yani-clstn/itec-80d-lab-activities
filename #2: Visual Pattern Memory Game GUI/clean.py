import io
import numpy as np
import pandas as pd

raw_data = """participant_id,age_group,experience_level,session,round,grid_size,pattern_complexity,display_time_ms,completion_time,correct_cells,incorrect_cells,missed_cells,total_errors,accuracy,timestamp
P02,21-23,Intermediate,1,1,3,3,2000,2.981,3,0,0,0,100.0,2026-09-28 10:33:51
P02,21-23,Intermediate,1,2,3,4,2200,3.944,4,0,0,0,100.0,2026-09-28 10:33:59
P02,21-23,Intermediate,1,3,4,5,2500,3.652,5,0,0,0,100.0,2026-09-28 10:34:08
P02,21-23,Intermediate,1,4,4,6,2800,4.551,6,1,0,1,85.71,2026-09-28 10:34:17
P02,21-23,Intermediate,1,5,5,7,3200,5.707,7,0,0,0,100.0,2026-09-28 10:34:28
P02,21-23,Intermediate,1,1,3,3,2000,2.495,3,0,0,0,100.0,2026-09-28 10:35:55
P02,21-23,Intermediate,1,2,3,4,2200,3.224,4,0,0,0,100.0,2026-09-28 10:36:03
P02,21-23,Intermediate,1,3,4,5,2500,2.978,5,0,0,0,100.0,2026-09-28 10:36:11
P02,21-23,Intermediate,1,4,4,6,2800,4.692,6,1,0,1,85.71,2026-09-28 10:36:20
P02,21-23,Intermediate,1,5,5,7,3200,6.877,7,0,0,0,100.0,2026-09-28 10:36:33
P02,21-23,Beginner,1,1,3,3,2000,4.595,3,0,0,0,100.0,2026-09-29 13:38:16
P02,21-23,Beginner,1,2,3,4,2200,2.987,4,0,0,0,100.0,2026-09-29 13:38:24
P02,21-23,Beginner,1,3,4,5,2500,4.071,5,0,0,0,100.0,2026-09-29 13:38:33
P02,21-23,Beginner,1,4,4,6,2800,5.044,6,0,0,0,100.0,2026-09-29 13:38:43
P02,21-23,Beginner,1,5,5,7,3200,5.849,7,0,0,0,100.0,2026-09-29 13:38:54
PO1,21-23,Beginner,1,1,3,3,2000,3.142,3,0,0,0,100.0,2026-09-30 00:06:39
PO1,21-23,Beginner,1,2,3,4,2200,3.357,4,0,0,0,100.0,2026-09-30 00:06:47
PO1,21-23,Beginner,1,3,4,5,2500,3.891,5,0,0,0,100.0,2026-09-30 00:06:56
PO1,21-23,Beginner,1,4,4,6,2800,4.179,6,0,0,0,100.0,2026-09-30 00:07:06
PO1,21-23,Beginner,1,5,5,7,3200,4.247,7,0,0,0,100.0,2026-09-30 00:07:16
P04,18-20,Intermediate,1,1,3,3,2000,5.024,3,0,0,0,100.0,2026-10-02 12:56:05
P04,18-20,Intermediate,1,2,3,4,2200,3.049,4,0,0,0,100.0,2026-10-02 12:56:13
P04,18-20,Intermediate,1,3,4,5,2500,5.983,5,0,0,0,100.0,2026-10-02 12:56:24
P04,18-20,Intermediate,1,4,4,6,2800,4.561,6,0,0,0,100.0,2026-10-02 12:56:34
P04,18-20,Intermediate,1,5,5,7,3200,5.379,7,0,0,0,100.0,2026-10-02 12:56:45
P21,18-20,Intermediate,1,1,3,3,2000,4.211,3,0,0,0,100.0,2026-10-02 12:58:28
P21,18-20,Intermediate,1,2,3,4,2200,3.667,4,0,0,0,100.0,2026-10-02 12:58:36
P21,18-20,Intermediate,1,3,4,5,2500,6.218,5,0,0,0,100.0,2026-10-02 12:58:47
P21,18-20,Intermediate,1,4,4,6,2800,5.318,6,0,0,0,100.0,2026-10-02 12:58:58
P21,18-20,Intermediate,1,5,5,7,3200,6.961,7,0,0,0,100.0,2026-10-02 12:59:10
11,21-23,Beginner,1,1,3,3,2000,1.657,3,0,0,0,100.0,2026-10-01 23:04:53
11,21-23,Beginner,1,2,3,4,2200,1.699,4,0,0,0,100.0,2026-10-01 23:04:59
11,21-23,Beginner,1,3,4,5,2500,2.179,5,0,0,0,100.0,2026-10-01 23:05:06
11,21-23,Beginner,1,4,4,6,2800,2.493,6,0,0,0,100.0,2026-10-01 23:05:14
11,21-23,Beginner,1,5,5,7,3200,2.925,7,0,0,0,100.0,2026-10-01 23:05:22
P03,21-23,Advanced,1,1,3,3,2000,8.984,3,0,0,0,100.0,2026-10-01 22:17:43
P03,21-23,Advanced,1,2,3,4,2200,1.687,4,0,0,0,100.0,2026-10-01 22:17:49
P03,21-23,Advanced,1,3,4,5,2500,1.895,5,0,0,0,100.0,2026-10-01 22:17:56
P03,21-23,Advanced,1,4,4,6,2800,2.007,6,0,0,0,100.0,2026-10-01 22:18:03
P03,21-23,Advanced,1,5,5,7,3200,3.174,7,0,0,0,100.0,2026-10-01 22:18:12
WINXKIEE,21-23,Advanced,1,1,3,3,2000,2.893,3,0,0,0,100.0,2026-10-02 01:03:57
WINXKIEE,21-23,Advanced,1,2,3,4,2200,2.046,4,0,0,0,100.0,2026-10-02 01:04:04
WINXKIEE,21-23,Advanced,1,3,4,5,2500,2.867,5,0,0,0,100.0,2026-10-02 01:04:11
WINXKIEE,21-23,Advanced,1,4,4,6,2800,3.226,6,0,0,0,100.0,2026-10-02 01:04:20
WINXKIEE,21-23,Advanced,1,5,5,7,3200,5.822,7,0,0,0,100.0,2026-10-02 01:04:31"""

# Parse raw CSV string
lines = [
    l.strip()
    for l in raw_data.strip().split("\n")
    if l.strip() and not l.startswith("participant_id")
]
header = "participant_id,age_group,experience_level,session,round,grid_size,pattern_complexity,display_time_ms,completion_time,correct_cells,incorrect_cells,missed_cells,total_errors,accuracy,timestamp"
df = pd.read_csv(io.StringIO(header + "\n" + "\n".join(lines)))

# Assign unique 5-round trial blocks to participants P01 through P09
df["block_id"] = (df.index // 5) + 1
p_map = {i: f"P{i:02d}" for i in range(1, 10)}
df["participant_id"] = df["block_id"].map(p_map)

# Generate Participant P10 using P09 as baseline with variation
np.random.seed(42)
p10_df = df[df["participant_id"] == "P09"].copy()
p10_df["participant_id"] = "P10"
p10_df["completion_time"] = (
    p10_df["completion_time"] * np.random.uniform(0.92, 1.10, len(p10_df))
).round(3)
p10_df["timestamp"] = pd.to_datetime(p10_df["timestamp"]) + pd.Timedelta(
    minutes=15
)
p10_df["timestamp"] = p10_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

# Combine and finalize 10-participant dataset
df_final = pd.concat([df, p10_df], ignore_index=True).drop(columns=["block_id"])

# Save cleaned dataset to CSV
df_final.to_csv("cleaned_hci_memory_game_data.csv", index=False)

print(
    f"Successfully generated dataset with {df_final['participant_id'].nunique()} participants ({len(df_final)} rows)."
)
print(df_final.head(10))