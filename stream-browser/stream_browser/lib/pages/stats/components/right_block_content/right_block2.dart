import 'package:flutter/material.dart';
import 'package:gif/gif.dart';
import 'package:provider/provider.dart';

import '../../../../constants/app_styles.dart';
import '../../../../services/file_provider.dart';
import '../../../../widgets/spacing.dart';
import '../encounter_timer.dart';

class RightBlock2 extends StatelessWidget {
  const RightBlock2({super.key});

  @override
  Widget build(BuildContext context) {
    int currTotalDens =
        context.select((FileProvider state) => state.currentTotalDens);
    int currEnc =
        context.select((FileProvider state) => state.switch2Encounters);

    String switch2GifNumber = context.select(
      (FileProvider state) => state.streamData?.switch2GifNumber ?? '1',
    );

    int? currStartTime = context.select(
      (FileProvider state) =>
          state.switch2CurrPokemon.startedHuntTimestamp?.toInt(),
    );
    int? currEndTime = context.select(
      (FileProvider state) => state.switch2CurrPokemon.caughtTimestamp?.toInt(),
    );

    int lastTotalDens =
        context.select((FileProvider state) => state.currentTotalDens);
    int lastEnc =
        context.select((FileProvider state) => state.switch2Encounters);

    String switch2GifNumberLast = context.select(
      (FileProvider state) => state.streamData?.switch2GifNumber ?? '1',
    );

    int? lastStartTime = context.select(
      (FileProvider state) =>
          state.switch2CurrPokemon.startedHuntTimestamp?.toInt(),
    );
    int? lastEndTime = context.select(
      (FileProvider state) => state.switch2CurrPokemon.caughtTimestamp?.toInt(),
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(
          'Shield',
          style: AppTextStyles.minecraftTen(fontSize: 36),
        ),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Last Shiny',
              style: AppTextStyles.pokePixel(fontSize: 36),
            ),
            Row(
              children: [
                Container(
                  width: 120,
                  height: 80,
                  child: Gif(
                    image: NetworkImage(
                      'https://raw.githubusercontent.com/adamsb0303/Shiny_Hunt_Tracker/master/Images/Sprites/3d/$switch2GifNumberLast.gif',
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
                            '$lastEnc',
                            style: AppTextStyles.pokePixel(fontSize: 48),
                          ),
                          HorizontalSpace(20),
                          Text(
                            '(Total: $lastTotalDens)',
                            style: AppTextStyles.pokePixel(fontSize: 20),
                          ),
                        ],
                      ),
                      EncounterTimer(
                        startTime: lastStartTime,
                        endTime: lastEndTime,
                        fontSize: 20,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ],
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
                        '$currEnc',
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
                    startTime: currStartTime,
                    endTime: currEndTime,
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
