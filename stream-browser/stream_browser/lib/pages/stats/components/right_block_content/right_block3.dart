import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../../constants/app_styles.dart';
import '../../../../services/file_provider.dart';
import '../../../../widgets/pokemon_row.dart';
import '../../../../widgets/scrolling_widget.dart';
import '../line_item.dart';

class RightBlock3 extends StatelessWidget {
  const RightBlock3({super.key});

  @override
  Widget build(BuildContext context) {
    final fileProvider = context.watch<FileProvider>();

    final phaseEncounters =
        (fileProvider.streamData?.switch2Targets ?? []).fold(
      0,
      (previousValue, element) =>
          previousValue +
          (fileProvider.getPokemonModel(element.name)?.totalEncounters ?? 0),
    );

    final phaseShinies = (fileProvider.streamData?.switch2Targets ?? []).fold(
      0,
      (previousValue, element) =>
          previousValue +
          (fileProvider.getPokemonModel(element.name)?.catches?.length ?? 0),
    );

    final targets = fileProvider.streamData?.switch2Targets ?? [];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(
          'Shield',
          style: AppTextStyles.minecraftTen(fontSize: 36),
        ),
        LineItem(leftText: 'Odds (Shiny charm)', rightText: '1/1365'),
        LineItem(
          leftText: 'Current total encounters',
          rightText: '$phaseEncounters',
        ),
        LineItem(leftText: 'Current total shinies', rightText: '$phaseShinies'),
        Center(
          child: targets.length > 3
              ? Container(
                  height: 175,
                  child: ScrollingWidget(
                    scrollSpeed: 30,
                    child: PokemonRow(
                      targets: targets,
                      pokemonGifSize: 90,
                    ),
                  ),
                )
              : PokemonRow(
                  targets: targets,
                  pokemonGifSize: 90,
                ),
        ),
      ],
    );
  }
}
