import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../models/pokemon.model.dart';
import '../../../models/stats.model.dart';
import '../../../services/file_provider.dart';
import '../../../components/line_item.dart';
import '../../../components/pokemon_display/pokemon_display.dart';

class DaDisplay extends StatelessWidget {
  const DaDisplay({
    required this.pokemon,
    super.key,
  });

  final List<PokemonModel> pokemon;

  @override
  Widget build(BuildContext context) {
    final StatsModel? pokemonStats =
        context.select((FileProvider e) => e.pokemonStats);

    String totalEncsLeftText = 'Total checks';
    int totalEncounters = pokemonStats?.totalDA ?? 0;

    String totalShiniesLeftText = 'Total shinies';
    int totalShinies = pokemonStats?.totalDAShinies ?? 0;

    String averageLeftText = 'Average checks';
    double averageEncounters = pokemonStats?.averageDA ?? 0;

    return Column(
      children: [
        LineItem(leftText: 'Odds (DA w Charm)', rightText: '1/100'),
        LineItem(leftText: totalEncsLeftText, rightText: '$totalEncounters'),
        LineItem(
          leftText: totalShiniesLeftText,
          rightText: '$totalShinies',
        ),
        LineItem(
          leftText: averageLeftText,
          rightText: averageEncounters.toStringAsFixed(2),
        ),
        Spacer(),
        PokemonDisplay(pokemon: pokemon),
      ],
    );
  }
}
