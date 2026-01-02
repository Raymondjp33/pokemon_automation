import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../../constants/app_styles.dart';
import '../../../../models/pokemon.model.dart';
import '../../../../services/file_provider.dart';
import '../pokemon_display/pokemon_display.dart';
import '../line_item.dart';

class LeftBlock4 extends StatelessWidget {
  const LeftBlock4({super.key});

  @override
  Widget build(BuildContext context) {
    final fileProvider = context.watch<FileProvider>();
    final List<PokemonModel> pokemon = fileProvider.switch1Pokemon;

    final phaseEncounters = pokemon.fold(
      0,
      (previousValue, element) => previousValue + element.encounters,
    );

    final phaseShinies = pokemon.fold(
      0,
      (previousValue, element) =>
          previousValue + (element.catches?.length ?? 0),
    );

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'shield',
          style: AppTextStyles.minecraftTen(fontSize: 32),
        ),
        LineItem(leftText: 'Odds (Shiny charm)', rightText: '1/1365'),
        LineItem(
          leftText: 'Current total encs',
          rightText: '$phaseEncounters',
        ),
        LineItem(leftText: 'Current total shinies', rightText: '$phaseShinies'),
        Spacer(),
        PokemonDisplay(pokemon: pokemon),
      ],
    );
  }
}
