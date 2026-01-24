import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../models/pokemon.model.dart';
import '../../../models/stats.model.dart';
import '../../../services/file_provider.dart';
import '../../../components/line_item.dart';
import '../../../components/pokemon_display/pokemon_display.dart';

class MainStatsDisplay extends StatelessWidget {
  const MainStatsDisplay({
    required this.pokemon,
    required this.screenContent,
    this.includeAverage = true,
    super.key,
  });

  final List<PokemonModel> pokemon;
  final String screenContent;
  final bool includeAverage;

  @override
  Widget build(BuildContext context) {
    final StatsModel? pokemonStats =
        context.select((FileProvider e) => e.pokemonStats);

    String oddsLeftText = '';
    String oddsRightText = '';

    String totalEncsLeftText = '';
    int totalEncounters = 0;

    String totalShiniesLeftText = '';
    int totalShinies = 0;

    String averageLeftText = '';
    double averageEncounters = 0;

    void setTexts() {
      switch (screenContent) {
        case 'egg':
          totalEncounters = pokemonStats?.totalEggs ?? 0;
          totalShinies = pokemonStats?.totalEggShinies ?? 0;
          averageEncounters = pokemonStats?.averageEggs ?? 0;
          oddsLeftText = 'Odds (Charm, Masuda)';
          oddsRightText = '1/512';
          totalEncsLeftText = 'Total hatched';
          totalShiniesLeftText = 'Total shinies';
          averageLeftText = 'Average hatched';
          break;

        case 'static':
          totalEncounters = pokemonStats?.totalStatic ?? 0;
          totalShinies = pokemonStats?.totalStaticShinies ?? 0;
          averageEncounters = pokemonStats?.averageStatic ?? 0;
          oddsLeftText = 'Odds (Static)';
          oddsRightText = '1/4096';
          totalEncsLeftText = 'Total static encs';
          totalShiniesLeftText = 'Total static shinies';
          averageLeftText = 'Average encs';
          break;

        case 'wild':
          totalEncounters = pokemonStats?.totalWild ?? 0;
          totalShinies = pokemonStats?.totalWildShinies ?? 0;
          averageEncounters = pokemonStats?.averageWild ?? 0;
          oddsLeftText = 'Odds (Shiny charm)';
          oddsRightText = '1/1365';
          totalEncsLeftText = 'Current total encs';
          totalShiniesLeftText = 'Current total shinies';
          averageLeftText = 'Average encs';
          break;

        case 'current':
        default:
          totalEncounters = pokemon.fold(
            0,
            (p, e) => p + e.encounters,
          );
          totalShinies = pokemon.fold(
            0,
            (p, e) => p + (e.catches?.length ?? 0),
          );
          averageEncounters = totalShinies == 0
              ? totalEncounters.toDouble()
              : totalEncounters / totalShinies;
          oddsLeftText = 'Odds (Shiny charm)';
          oddsRightText = '1/1365';
          totalEncsLeftText = 'Current total encs';
          totalShiniesLeftText = 'Current total shinies';
          averageLeftText = 'Average encs';

          break;
      }
    }

    setTexts();

    return Column(
      children: [
        LineItem(leftText: oddsLeftText, rightText: oddsRightText),
        LineItem(leftText: totalEncsLeftText, rightText: '$totalEncounters'),
        LineItem(
          leftText: totalShiniesLeftText,
          rightText: '$totalShinies',
        ),
        if (includeAverage)
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
