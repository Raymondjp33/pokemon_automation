import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../../constants/app_styles.dart';
import '../../../../models/pokemon.model.dart';
import '../../../../models/target.model.dart';
import '../../../../services/file_provider.dart';
import '../../../../widgets/pokemon_gif_image.dart';
import '../../../../widgets/scrolling_widget.dart';
import '../line_item.dart';

class RightBlock1 extends StatelessWidget {
  const RightBlock1({super.key});

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

    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(
          'Shield',
          style: AppTextStyles.minecraftTen(fontSize: 36),
        ),
        LineItem(leftText: 'Odds (Shiny charm)', rightText: '1/1365'),
        LineItem(leftText: 'Phase encounters', rightText: '$phaseEncounters'),
        LineItem(leftText: 'Phase shinies', rightText: '$phaseShinies'),
        Container(
          height: 175,
          child: ScrollingWidget(
            scrollSpeed: 30,
            child: Row(
              children: [
                for (TargetModel target
                    in fileProvider.streamData?.switch2Targets ?? [])
                  Builder(
                    builder: (context) {
                      PokemonModel? pokemonModel =
                          fileProvider.getPokemonModel(target.name);

                      if (pokemonModel == null) {
                        return Container();
                      }

                      return Container(
                        padding: EdgeInsets.symmetric(horizontal: 10),
                        decoration: BoxDecoration(
                          border: Border.symmetric(
                            vertical: BorderSide(color: Colors.black54),
                          ),
                        ),
                        child: Column(
                          children: [
                            PokemonGifImage(
                              width: 100,
                              height: 100,
                              dexNum: target.dexNum,
                            ),
                            Text(
                              '${pokemonModel.totalEncounters}',
                              style: AppTextStyles.pokePixel(fontSize: 40),
                            ),
                            Text(
                              '${pokemonModel.catches?.length ?? 0}/${target.target} ${target.mainTarget ? "(Target)" : ''}',
                              style: AppTextStyles.pokePixel(fontSize: 24),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}
