import 'package:flutter/material.dart';
import 'package:gif/gif.dart';
import 'package:provider/provider.dart';

import '../../../constants/app_styles.dart';
import '../../../services/file_provider.dart';
import '../../../widgets/pokemon_row.dart';
import '../../../widgets/scrolling_widget.dart';
import '../../../widgets/spacing.dart';
import '../../stats/components/encounter_timer.dart';

class Switch2Content extends StatelessWidget {
  const Switch2Content({super.key});

  @override
  Widget build(BuildContext context) {
    int currentEncounters =
        context.select((FileProvider e) => e.switch2CurrentEncounters);
    String shinyCounts =
        context.select((FileProvider e) => e.switch2ShinyCounts);
    String switch2GifNumber =
        context.select((FileProvider e) => e.switch2GifNumber);
    int? startTime = context.select((FileProvider e) => e.switch2StartTime);

    final fileProvider = context.watch<FileProvider>();
    final targets = fileProvider.streamData?.switch2Targets ?? [];
    final screenIndex =
        context.select((FileProvider state) => state.rightScreenIndex);

    if (screenIndex == 0) {
      return Center(
        child: targets.length > 3
            ? Container(
                height: 175,
                padding: EdgeInsets.symmetric(vertical: 10),
                child: ScrollingWidget(
                  scrollSpeed: 30,
                  child: PokemonRow(
                    targets: targets,
                    pokemonGifSize: 80,
                  ),
                ),
              )
            : Padding(
                padding: EdgeInsets.only(top: 10),
                child: PokemonRow(
                  targets: targets,
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
