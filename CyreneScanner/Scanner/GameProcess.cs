using System.Diagnostics;

namespace CyreneScanner.Scanner;

public static class GameProcess
{
    private static readonly string[] ProcessNames =
    {
        "GenshinImpact",
        "YuanShen"
    };

    public static Process? Find()
    {
        foreach (var processName in ProcessNames)
        {
            var processes = Process.GetProcessesByName(
                processName
            );

            if (processes.Length > 0)
            {
                return processes[0];
            }
        }

        return null;
    }
}