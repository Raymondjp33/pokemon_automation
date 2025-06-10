import 'package:flutter/material.dart';
import 'package:gif/gif.dart';
import 'package:provider/provider.dart';

import '../../../../constants/app_styles.dart';
import '../../../../services/file_provider.dart';
import '../../../../widgets/spacing.dart';
import '../encounter_timer.dart';
import '../line_item.dart';

class LeftBlock1 extends StatelessWidget {
  const LeftBlock1({super.key});

  @override
  Widget build(BuildContext context) {
    int currentEncounters =
        context.select((FileProvider e) => e.switch1CurrentEncounters);
    String shinyCounts =
        context.select((FileProvider e) => e.switch1ShinyCounts);
    String switch1GifNumber =
        context.select((FileProvider e) => e.switch1GifNumber);
    int totalShinies =
        context.select((FileProvider e) => e.switch1TotalShinies);
    int totalEncounters = context.select((FileProvider e) => e.switch1TotalEnc);
    double averageEncounters =
        context.select((FileProvider e) => e.switch1AverageEnc);
    int? startTime = context.select((FileProvider e) => e.switch1StartTime);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'BRILLIANT DIAMOND',
          style: AppTextStyles.minecraftTen(fontSize: 32),
        ),
        LineItem(leftText: 'Odds (Shiny charm, Masuda)', rightText: '1/512'),
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
