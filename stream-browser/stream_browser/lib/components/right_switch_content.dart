import 'package:flutter/material.dart';
import 'package:gif/gif.dart';
import 'package:provider/provider.dart';

import '../constants/app_styles.dart';
import '../services/file_provider.dart';
import '../widgets/spacing.dart';
import 'line_item.dart';

class RightSwitchContent extends StatelessWidget {
  const RightSwitchContent({super.key});

  @override
  Widget build(BuildContext context) {
    int totalDens =
        context.select((FileProvider state) => state.switch2TotalDens);
    int currTotalDens =
        context.select((FileProvider state) => state.currentTotalDens);
    int enc = context.select((FileProvider state) => state.switch2Encounters);
    int totalLegends =
        context.select((FileProvider state) => state.switch2LegendaryShinies);
    double switch2AverageChecks =
        context.select((FileProvider state) => state.switch2AverageChecks);
    String switch2GifNumber = context.select(
      (FileProvider state) => state.streamData?.switch2GifNumber ?? '1',
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(
          'Shield',
          style: AppTextStyles.minecraftTen(fontSize: 36),
        ),
        LineItem(leftText: 'Odds', rightText: '1/100'),
        // LineItem(leftText: 'Normal shinies', rightText: '60'),
        LineItem(leftText: 'Legendary shinies', rightText: '$totalLegends'),
        LineItem(leftText: 'Total dens', rightText: '$totalDens'),
        LineItem(
          leftText: 'Average checks',
          rightText: switch2AverageChecks.toStringAsFixed(2),
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
                  'https://raw.githubusercontent.com/adamsb0303/Shiny_Hunt_Tracker/master/Images/Sprites/3d/$switch2GifNumber.gif',
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
                        '$enc',
                        style: AppTextStyles.pokePixel(fontSize: 60),
                      ),
                      HorizontalSpace(20),
                      Text(
                        '(Total dens: $currTotalDens)',
                        style: AppTextStyles.pokePixel(fontSize: 30),
                      ),
                    ],
                  ),
                  Switch2EncounterTimer(),
                ],
              ),
            ),
          ],
        ),
      ],
    );
  }
}

class Switch2EncounterTimer extends StatelessWidget {
  const Switch2EncounterTimer({super.key});

  @override
  Widget build(BuildContext context) {
    final fileProvider = context.watch<FileProvider>();
    DateTime now = DateTime.now();

    num? startTime = fileProvider.switch2CurrPokemon.startedHuntTimestamp;
    int endTime = fileProvider.switch2CurrPokemon.caughtTimestamp?.toInt() ??
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
