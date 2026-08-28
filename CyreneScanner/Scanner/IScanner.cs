namespace CyreneScanner.Scanner;

public interface IScanner
{
    Task<object?> ScanAsync(
        CancellationToken cancellationToken = default
    );
}