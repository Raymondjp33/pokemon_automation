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

class LeftBlock1 extends StatelessWidget {
  const LeftBlock1({super.key});

  @override
  Widget build(BuildContext context) {
    final FileProvider fileProvider = context.watch<FileProvider>();
    final PokemonModel? pokemon = fileProvider.switch1Pokemon.firstOrNull;
    final StatsModel? pokemonStats = fileProvider.pokemonStats;

    int currentEncounters = pokemon?.encounters ?? 0;
    String shinyCounts =
        '${(pokemon?.catches ?? []).length}/${pokemon?.targets ?? 0}';
    String switch1GifNumber = '${(pokemon?.pokemonId ?? 1) - 1}';
    int totalShinies = pokemonStats?.totalEggShinies ?? 0;
    int totalEncounters = pokemonStats?.totalEggs ?? 0;
    double averageEncounters = pokemonStats?.averageEggs ?? 0;

    int? startTime = pokemon?.startedHuntTimestamp?.toInt();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'SHIELD',
          style: AppTextStyles.minecraftTen(fontSize: 32),
        ),
        LineItem(leftText: 'Odds (Charm, Masuda)', rightText: '1/512'),
        LineItem(leftText: 'Total shinies', rightText: '$totalShinies'),
        LineItem(leftText: 'Total hatched', rightText: '$totalEncounters'),
        LineItem(
          leftText: 'Average hatched',
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
