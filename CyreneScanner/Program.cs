using CyreneScanner.Scanner;

Console.WriteLine("CyreneScanner v1.0.0");
Console.WriteLine("=====================");
Console.WriteLine();

var game = GameProcess.Find();

if (game is null)
{
    Console.WriteLine(
        "Genshin Impact is not currently running."
    );
}
else
{
    Console.WriteLine(
        $"Genshin Impact detected [PID: {game.Id}]."
    );
}