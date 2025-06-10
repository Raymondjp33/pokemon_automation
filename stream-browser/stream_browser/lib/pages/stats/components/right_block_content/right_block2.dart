import 'package:flutter/material.dart';
import 'package:gif/gif.dart';
import 'package:provider/provider.dart';

import '../../../../constants/app_styles.dart';
import '../../../../services/file_provider.dart';
import '../../../../widgets/spacing.dart';
import '../encounter_timer.dart';
import '../line_item.dart';

class RightBlock2 extends StatelessWidget {
  const RightBlock2({super.key});

  @override
  Widget build(BuildContext context) {
    int currentEncounters =
        context.select((FileProvider e) => e.switch2CurrentEncounters);
    String shinyCounts =
        context.select((FileProvider e) => e.switch2ShinyCounts);
    String switch2GifNumber =
        context.select((FileProvider e) => e.switch2GifNumber);
    int totalShinies =
        context.select((FileProvider e) => e.switch2TotalShinies);
    int totalEncounters = context.select((FileProvider e) => e.switch2TotalEnc);
    double averageEncounters =
        context.select((FileProvider e) => e.switch2AverageEnc);
    int? startTime = context.select((FileProvider e) => e.switch2StartTime);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(
          'shield',
          style: AppTextStyles.minecraftTen(fontSize: 32),
        ),
        LineItem(leftText: 'Odds (Shiny charm)', rightText: '1/1365'),
        LineItem(leftText: 'Total wild shinies', rightText: '$totalShinies'),
        LineItem(
          leftText: 'Total wild encounters',
          rightText: '$totalEncounters',
        ),
        LineItem(
          leftText: 'Average wild encounters',
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
                  EncounterTimer(
                    startTime: startTime,
                    endTime: null,
                  ),
                ],
              ),
            ),
          ],
        ),
      ],
    );
  }
}
