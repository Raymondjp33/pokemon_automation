import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../components/bordered_box.dart';
import '../../components/main_background.dart';
import '../../models/pokemon.model.dart';
import '../../services/file_provider.dart';
import 'components/middle_content.dart';
import 'components/switch_content.dart';

class TwoSwitchView extends StatelessWidget {
  const TwoSwitchView({super.key});

  @override
  Widget build(BuildContext context) {
    String screen1Content =
        context.select((FileProvider state) => state.switch1Content);
    String game1Name =
        context.select((FileProvider state) => state.switch1Game);
    List<PokemonModel> pokemon1 =
        context.select((FileProvider state) => state.switch1Pokemon);

    String screen2Content =
        context.select((FileProvider state) => state.switch2Content);
    String game2Name =
        context.select((FileProvider state) => state.switch2Game);
    List<PokemonModel> pokemon2 =
        context.select((FileProvider state) => state.switch2Pokemon);

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
                  height: 363,
                  child: Row(
                    children: [
                      BorderedBox(
                        width: 640,
                        right: 2.5,
                        filled: true,
                      ),
                      BorderedBox(
                        width: 640,
                        left: 2.5,
                        filled: true,
                      ),
                    ],
                  ),
                ),
                Positioned(
                  bottom: 0,
                  height: 357,
                  child: Row(
                    children: [
                      BorderedBox(
                        width: 328,
                        right: 0,
                        top: 0,
                        padding:
                            EdgeInsets.symmetric(vertical: 10, horizontal: 20),
                        child: SwitchContent(
                          screenContent: screen1Content,
                          gameName: game1Name,
                          pokemon: pokemon1,
                        ),
                      ),
                      BorderedBox(
                        width: 624,
                        left: 5,
                        right: 5,
                        top: 0,
                        padding:
                            EdgeInsets.symmetric(vertical: 10, horizontal: 2),
                        child: MiddleContent(),
                      ),
                      BorderedBox(
                        width: 328,
                        left: 0,
                        top: 0,
                        padding:
                            EdgeInsets.symmetric(vertical: 10, horizontal: 20),
                        child: SwitchContent(
                          screenContent: screen2Content,
                          gameName: game2Name,
                          pokemon: pokemon2,
                        ),
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
