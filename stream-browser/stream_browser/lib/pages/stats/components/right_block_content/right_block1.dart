import 'package:flutter/material.dart';
import 'package:gif/gif.dart';
import 'package:provider/provider.dart';

import '../../../../constants/app_styles.dart';
import '../../../../services/file_provider.dart';
import '../../../../widgets/spacing.dart';
import '../encounter_timer.dart';
import '../line_item.dart';

class RightBlock1 extends StatelessWidget {
  const RightBlock1({super.key});

  @override
  Widget build(BuildContext context) {
    final totalEggs = context.select((FileProvider e) => e.switch2TotalEggs);
    final totalEggShinies =
        context.select((FileProvider e) => e.switch2TotalEggShinies);
    final averageEggs =
        context.select((FileProvider e) => e.switch2AverageEggs);

    final switch2GifNumber =
        context.select((FileProvider e) => e.switch2GifNumber);
    final currentEnc =
        context.select((FileProvider e) => e.switch2CurrentEncounters);
    final shinyCounts =
        context.select((FileProvider e) => e.switch2ShinyCounts);
    final startTime = context.select((FileProvider e) => e.switch2StartTime);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(
          'Shield',
          style: AppTextStyles.minecraftTen(fontSize: 36),
        ),
        LineItem(leftText: 'Odds (Shiny charm, Masuda)', rightText: '1/512'),
        LineItem(leftText: 'Total egg shinies', rightText: '$totalEggShinies'),
        LineItem(leftText: 'Total eggs hatched', rightText: '$totalEggs'),
        LineItem(
          leftText: 'Average eggs hatched',
          rightText: averageEggs.toStringAsFixed(2),
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
                        '$currentEnc',
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
