import 'package:flutter/material.dart';
import 'package:gif/gif.dart';
import 'package:provider/provider.dart';

import '../constants/app_styles.dart';
import '../services/file_provider.dart';
import '../widgets/spacing.dart';
import 'line_item.dart';

class LeftSwitchContent extends StatelessWidget {
  const LeftSwitchContent({super.key});

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

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'BRILLIANT DIAMOND',
          style: AppTextStyles.minecraftTen(fontSize: 32),
        ),
        LineItem(leftText: 'Odds', rightText: '1/4096'),
        LineItem(leftText: 'Total shinies', rightText: '$totalShinies'),
        LineItem(leftText: 'Total encounters', rightText: '$totalEncounters'),
        LineItem(
          leftText: 'Average encounters',
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
                  Text(
                    '$currentEncounters',
                    style: AppTextStyles.pokePixel(fontSize: 60),
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
    num? startTime = fileProvider.switch1CurrPokemon.startedHuntTimestamp;

    DateTime now = DateTime.now();
    if (startTime == null) {
      return Container();
    }

    Duration timeDifference =
        Duration(milliseconds: now.millisecondsSinceEpoch - startTime.toInt());
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
