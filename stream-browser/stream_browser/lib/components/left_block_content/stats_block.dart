import 'package:flutter/material.dart';
import 'package:gif/gif.dart';
import 'package:provider/provider.dart';

import '../../constants/app_styles.dart';
import '../../services/file_provider.dart';
import '../../widgets/spacing.dart';
import '../line_item.dart';

class StatsBlock extends StatelessWidget {
  const StatsBlock({super.key});

  @override
  Widget build(BuildContext context) {
    int totalShinies =
        context.select((FileProvider state) => state.switch1TotalShinies);
    int totalEncounters =
        context.select((FileProvider state) => state.switch1TotalEncounters);
    double averageEncounters =
        context.select((FileProvider state) => state.switch1AverageEncounters);
    int currentEncounters =
        context.select((FileProvider state) => state.switch1Encounters);
    String switch1GifNumber = context.select(
      (FileProvider state) => state.streamData?.switch1GifNumber ?? '1',
    );
    String shinyCounts = context.select(
      (FileProvider state) => state.shinyCounts,
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'BRILLIANT DIAMOND',
          style: AppTextStyles.minecraftTen(fontSize: 32),
        ),
        LineItem(leftText: 'Odds (No charm, Masuda)', rightText: '1/683'),
        LineItem(leftText: 'Total egg shinies', rightText: '$totalShinies'),
        LineItem(leftText: 'Total eggs hatched', rightText: '$totalEncounters'),
        LineItem(
          leftText: 'Average eggs hatched',
          rightText: averageEncounters.toStringAsFixed(2),
        ),
        Spacer(),
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 150,
              height: 108,
              child: Gif(
                image: NetworkImage(
                  'https://raw.githubusercontent.com/adamsb0303/Shiny_Hunt_Tracker/master/Images/Sprites/3d/$switch1GifNumber.gif',
                ),
                fit: BoxFit.contain,
                autostart: Autostart.loop,
              ),
            ),
            HorizontalSpace(10),
            Flexible(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        '$currentEncounters',
                        style: AppTextStyles.pokePixel(fontSize: 60),
                      ),
                      HorizontalSpace(30),
                      Text(
                        shinyCounts,
                        style: AppTextStyles.pokePixel(fontSize: 40),
                      ),
                    ],
                  ),
                  Switch1EncounterTimer(),
                ],
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class Switch1EncounterTimer extends StatelessWidget {
  const Switch1EncounterTimer({super.key});

  @override
  Widget build(BuildContext context) {
    final fileProvider = context.watch<FileProvider>();
    DateTime now = DateTime.now();

    num? startTime = fileProvider.switch1CurrPokemon.startedHuntTimestamp;
    int endTime = fileProvider.switch1CurrPokemon.caughtTimestamp?.toInt() ??
        now.millisecondsSinceEpoch;

    if (startTime == null) {
      return Container();
    }

    Duration timeDifference =
        Duration(milliseconds: endTime - startTime.toInt());
    return Text(
      formatDuration(timeDifference),
      style: AppTextStyles.pokePixel(fontSize: 24),
    );
  }
}

String formatDuration(Duration duration) {
  int days = duration.inDays;
  int hours = duration.inHours % 24;
  int minutes = duration.inMinutes % 60;
  int seconds = duration.inSeconds % 60;

  final parts = <String>[];
  if (days > 0) parts.add('${days}d');
  if (hours > 0) parts.add('${hours}h');
  if (minutes > 0) parts.add('${minutes}m');
  if (seconds > 0 || parts.isEmpty) parts.add('${seconds}s');

  return parts.join(' ');
}
