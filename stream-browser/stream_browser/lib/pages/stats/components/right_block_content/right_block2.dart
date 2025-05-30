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

    int? startTime = context.select(
      (FileProvider state) =>
          state.switch2CurrPokemon.startedHuntTimestamp?.toInt(),
    );
    int? endTime = context.select(
      (FileProvider state) => state.switch2CurrPokemon.caughtTimestamp?.toInt(),
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(
          'Shield',
          style: AppTextStyles.minecraftTen(fontSize: 36),
        ),
        LineItem(leftText: 'Odds (Shiny charm)', rightText: '1/1365'),
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
                useCache: false,
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
                        '(Total: $currTotalDens)',
                        style: AppTextStyles.pokePixel(fontSize: 30),
                      ),
                    ],
                  ),
                  EncounterTimer(
                    startTime: startTime,
                    endTime: endTime,
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
