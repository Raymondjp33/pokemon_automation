import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../../constants/app_styles.dart';
import '../../../../models/pokemon.model.dart';
import '../../../../models/stats.model.dart';
import '../../../../services/file_provider.dart';
import '../line_item.dart';
import '../pokemon_display/pokemon_display.dart';

class RightBlock2 extends StatelessWidget {
  const RightBlock2({super.key});

  @override
  Widget build(BuildContext context) {
    final List<PokemonModel> pokemon =
        context.select((FileProvider e) => e.switch2Pokemon);
    final StatsModel? pokemonStats =
        context.select((FileProvider e) => e.pokemonStats);

    int totalShinies = pokemonStats?.totalWildShinies ?? 0;
    int totalEncounters = pokemonStats?.totalWild ?? 0;
    double averageEncounters = pokemonStats?.averageWild ?? 0;

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
        PokemonDisplay(pokemon: pokemon),
      ],
    );
  }
}
