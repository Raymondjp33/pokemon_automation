import 'package:flutter/material.dart';
import 'package:gif/gif.dart';
import 'package:provider/provider.dart';

import '../../../../constants/app_styles.dart';
import '../../../../models/pokemon.model.dart';
import '../../../../models/stats.model.dart';
import '../../../../services/file_provider.dart';
import '../../../../widgets/spacing.dart';

import '../encounter_timer.dart';
import '../line_item.dart';

class RightBlock1 extends StatelessWidget {
  const RightBlock1({super.key});

  @override
  Widget build(BuildContext context) {
    final FileProvider fileProvider = context.watch<FileProvider>();
    final PokemonModel? pokemon = fileProvider.switch2Pokemon.firstOrNull;
    final StatsModel? pokemonStats = fileProvider.pokemonStats;

    int currentEnc = pokemon?.encounters ?? 0;
    String switch2GifNumber = '${(pokemon?.pokemonId ?? 1) - 1}';
    String shinyCounts =
        '${(pokemon?.catches ?? []).length}/${pokemon?.targets ?? 0}';
    int totalShinies = pokemonStats?.totalStaticShinies ?? 0;
    int totalEncounters = pokemonStats?.totalStatic ?? 0;
    double averageEncounters = pokemonStats?.averageStatic ?? 0;
    int? startTime = pokemon?.startedHuntTimestamp?.toInt();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(
          'Shield',
          style: AppTextStyles.minecraftTen(fontSize: 36),
        ),
        LineItem(leftText: 'Odds (Static)', rightText: '1/4096'),
        LineItem(leftText: 'Total static shinies', rightText: '$totalShinies'),
        LineItem(leftText: 'Total static encs', rightText: '$totalEncounters'),
        LineItem(
          leftText: 'Average encs',
          rightText: averageEncounters.toStringAsFixed(2),
        ),
        Spacer(),
        Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: 100,
              height: 100,
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
