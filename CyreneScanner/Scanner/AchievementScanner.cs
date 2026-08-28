namespace CyreneScanner.Scanner;

public sealed class AchievementScanner: IScanner
{
    public async Task<object?> ScanAsync(
        CancellationToken cancellationToken = default
    )
    {
        await Task.CompletedTask;

        return new
        {
            achievements = Array.Empty<object>()
        };
    }
}