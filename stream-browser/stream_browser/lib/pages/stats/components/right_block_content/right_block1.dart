import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../../constants/app_styles.dart';
import '../../../../models/pokemon.model.dart';
import '../../../../models/stats.model.dart';
import '../../../../services/file_provider.dart';

import '../line_item.dart';
import '../pokemon_display/pokemon_display.dart';

class RightBlock1 extends StatelessWidget {
  const RightBlock1({super.key});

  @override
  Widget build(BuildContext context) {
    final List<PokemonModel> switch2Pokemon =
        context.select((FileProvider e) => e.switch2Pokemon);
    final StatsModel? pokemonStats =
        context.select((FileProvider e) => e.pokemonStats);

    int totalShinies = pokemonStats?.totalStaticShinies ?? 0;
    int totalEncounters = pokemonStats?.totalStatic ?? 0;
    double averageEncounters = pokemonStats?.averageStatic ?? 0;

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
        PokemonDisplay(pokemon: switch2Pokemon),
      ],
    );
  }
}
