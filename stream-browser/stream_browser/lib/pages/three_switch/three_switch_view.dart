import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../components/bordered_box.dart';
import '../../components/main_background.dart';
import '../../constants/app_styles.dart';
import '../../models/display_content.model.dart';
import '../../models/pokemon.model.dart';
import '../../services/file_provider.dart';
import '../two_switch/components/middle_content.dart';
import '../two_switch/components/switch_content.dart';

class ThreeSwitchView extends StatelessWidget {
  const ThreeSwitchView({super.key});

  @override
  Widget build(BuildContext context) {
    final fileProvider = context.watch<FileProvider>();

    DisplayContent? screen1Content = fileProvider.switch1Content;
    List<PokemonModel> pokemon1 = fileProvider.switch1Pokemon;

    DisplayContent? screen2Content = fileProvider.switch2Content;
    List<PokemonModel> pokemon2 = fileProvider.switch2Pokemon;

    DisplayContent? screen3Content = fileProvider.switch3Content;
    List<PokemonModel> pokemon3 = fileProvider.switch3Pokemon;

    DateTime now = DateTime.now();

    // Random int is stream starttime in ms
    Duration timeDifference = Duration(
      milliseconds: now.millisecondsSinceEpoch - 1741255200000,
    );

    return Scaffold(
      body: Center(
        child: Container(
          width: 1280,
          height: 720,
          decoration: BoxDecoration(),
          child: Center(
            // STACK
            child: MainBackground(
              children: [
                Positioned(
                  top: 0,
                  height: 437,
                  child: Row(
                    children: [
                      Column(
                        children: [
                          BorderedBox(
                            bottom: 0,
                            height: 137,
                            width: 308,
                            padding: EdgeInsets.symmetric(vertical: 10),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(
                                  formatDateTime(now),
                                  style: AppTextStyles.minecraftTen(
                                    fontSize: 32,
                                  ),
                                ),
                                Text(
                                  'IM AWAY',
                                  style: AppTextStyles.minecraftTen(
                                    fontSize: 32,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          BorderedBox(
                            bottom: 0,
                            width: 308,
                            height: 300,
                            padding: EdgeInsets.symmetric(
                              horizontal: 5,
                              vertical: 15,
                            ),
                            child: SwitchContent(
                              screenContent: screen1Content,
                              pokemon: pokemon1,
                              includeAverage:
                                  screen1Content?.huntType != 'current',
                              includeTitle: false,
                            ),
                          ),
                        ],
                      ),
                      Column(
                        children: [
                          BorderedBox(
                            width: 664,
                            height: 382,
                            left: 0,
                            right: 0,
                            filled: true,
                          ),
                          Container(
                            width: 664,
                            height: 55,
                            padding: EdgeInsets.symmetric(horizontal: 20),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              crossAxisAlignment: CrossAxisAlignment.center,
                              children: [
                                Text(
                                  screen1Content?.game ?? '',
                                  style: AppTextStyles.minecraftTen(
                                    fontSize: 32,
                                  ),
                                ),
                                Text(
                                  screen2Content?.game ?? '',
                                  style: AppTextStyles.minecraftTen(
                                    fontSize: 32,
                                  ),
                                ),
                                Text(
                                  screen3Content?.game ?? '',
                                  style: AppTextStyles.minecraftTen(
                                    fontSize: 32,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                      Column(
                        children: [
                          BorderedBox(
                            bottom: 0,
                            height: 137,
                            width: 308,
                            padding: EdgeInsets.symmetric(vertical: 10),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(
                                  'Stream Runtime',
                                  style: AppTextStyles.minecraftTen(
                                    fontSize: 32,
                                  ),
                                ),
                                Text(
                                  formatDuration(timeDifference),
                                  style: AppTextStyles.pokePixel(fontSize: 32),
                                ),
                              ],
                            ),
                          ),
                          BorderedBox(
                            bottom: 0,
                            width: 308,
                            height: 300,
                            padding: EdgeInsets.symmetric(
                              horizontal: 5,
                              vertical: 15,
                            ),
                            child: SwitchContent(
                              screenContent: screen3Content,
                              pokemon: pokemon3,
                              includeAverage:
                                  screen3Content?.huntType != 'current',
                              includeTitle: false,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                Positioned(
                  bottom: 0,
                  height: 283,
                  child: Row(
                    children: [
                      BorderedBox(
                        width: 500,
                        filled: true,
                      ),
                      BorderedBox(
                        width: 280,
                        left: 0,
                        right: 0,
                        top: 0,
                        padding:
                            EdgeInsets.symmetric(horizontal: 5, vertical: 15),
                        child: SwitchContent(
                          screenContent: screen2Content,
                          pokemon: pokemon2,
                          includeAverage: screen2Content?.huntType != 'current',
                          includeTitle: false,
                        ),
                      ),
                      BorderedBox(
                        width: 500,
                        filled: true,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
