import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../../constants/app_styles.dart';
import '../../../../models/pokemon.model.dart';
import '../../../../models/stats.model.dart';
import '../../../../services/file_provider.dart';
import '../line_item.dart';
import '../pokemon_display/pokemon_display.dart';

class RightBlock4 extends StatelessWidget {
  const RightBlock4({super.key});

  @override
  Widget build(BuildContext context) {
    final FileProvider fileProvider = context.watch<FileProvider>();
    final List<PokemonModel> pokemon = fileProvider.switch2Pokemon;
    final StatsModel? pokemonStats = fileProvider.pokemonStats;

    int totalShinies = pokemonStats?.totalEggShinies ?? 0;
    int totalEncounters = pokemonStats?.totalEggs ?? 0;
    double averageEncounters = pokemonStats?.averageEggs ?? 0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(
          'Violet',
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
        PokemonDisplay(pokemon: pokemon),
      ],
    );
  }
}
