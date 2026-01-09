import 'package:flutter/material.dart';
import 'package:gif/gif.dart';
import 'package:provider/provider.dart';

import '../../../constants/app_styles.dart';
import '../../../models/pokemon.model.dart';
import '../../../services/file_provider.dart';
import '../../stats/components/pokemon_display/pokemon_row.dart';
import '../../../widgets/scrolling_widget.dart';
import '../../../widgets/spacing.dart';
import '../../stats/components/encounter_timer.dart';

class Switch2Content extends StatelessWidget {
  const Switch2Content({super.key});

  @override
  Widget build(BuildContext context) {
    final List<PokemonModel>? pokemon =
        context.select((FileProvider e) => e.switch2Pokemon);

    int currentEncounters = pokemon?.firstOrNull?.encounters ?? 0;
    String shinyCounts =
        '${pokemon?.firstOrNull?.catches?.length ?? 0}/${pokemon?.firstOrNull?.targets ?? 0}';
    String switch2GifNumber = '${pokemon?.first.gifNumber ?? 1}';
    int? startTime = pokemon?.firstOrNull?.startedHuntTimestamp?.toInt();

    final screenIndex =
        context.select((FileProvider state) => state.rightScreenContent);

    // FIX THIS
    if (screenIndex == '') {
      return Center(
        child: (pokemon?.length ?? 0) > 3
            ? Container(
                height: 175,
                padding: EdgeInsets.symmetric(vertical: 10),
                child: ScrollingWidget(
                  scrollSpeed: 30,
                  child: PokemonRow(
                    targets: pokemon,
                    pokemonGifSize: 80,
                  ),
                ),
              )
            : Padding(
                padding: EdgeInsets.only(top: 10),
                child: PokemonRow(
                  targets: pokemon,
                  pokemonGifSize: 80,
                ),
              ),
      );
    }

    return Row(
      children: [
        Container(
          width: 120,
          height: 108,
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
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Row(
                children: [
                  Text(
                    '$currentEncounters',
                    style: AppTextStyles.pokePixel(fontSize: 52),
                  ),
                  HorizontalSpace(30),
                  Text(
                    shinyCounts,
                    style: AppTextStyles.pokePixel(fontSize: 32),
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
    );
  }
}
