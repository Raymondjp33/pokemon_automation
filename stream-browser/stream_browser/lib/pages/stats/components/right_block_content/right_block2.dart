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

class RightBlock2 extends StatelessWidget {
  const RightBlock2({super.key});

  @override
  Widget build(BuildContext context) {
    final PokemonModel? pokemon =
        context.select((FileProvider e) => e.switch2Pokemon.firstOrNull);
    final StatsModel? pokemonStats =
        context.select((FileProvider e) => e.pokemonStats);

    int currentEncounters = pokemon?.encounters ?? 0;
    String shinyCounts =
        '${(pokemon?.catches ?? []).length}/${pokemon?.targets ?? 0}';
    String switch2GifNumber = '${pokemon?.gifNumber ?? 1}';
    int totalShinies = pokemonStats?.totalWildShinies ?? 0;
    int totalEncounters = pokemonStats?.totalWild ?? 0;
    double averageEncounters = pokemonStats?.averageWild ?? 0;
    int? startTime = pokemon?.startedHuntTimestamp?.toInt();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(
          'shield',
          style: AppTextStyles.minecraftTen(fontSize: 32),
        ),
        LineItem(leftText: 'Odds (Shiny charm)', rightText: '1/1365'),
        LineItem(leftText: 'Total shinies', rightText: '$totalShinies'),
        LineItem(
          leftText: 'Total enc',
          rightText: '$totalEncounters',
        ),
        LineItem(
          leftText: 'Average enc',
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
