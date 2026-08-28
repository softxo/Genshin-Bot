namespace CyreneScanner.Models;

public sealed class AchievementRecord
{
    public int GenshinId { get; init; }

    public int? Status { get; init; }

    public int? Current { get; init; }

    public int? Total { get; init; }

    public long? Timestamp { get; init; }
}