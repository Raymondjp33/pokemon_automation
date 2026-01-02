import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../../services/file_provider.dart';
import 'left_block1.dart';
import 'left_block2.dart';
import 'left_block3.dart';
import 'left_block4.dart';

class LeftSwitchContent extends StatelessWidget {
  const LeftSwitchContent({super.key});

  @override
  Widget build(BuildContext context) {
    int screenIndex =
        context.select((FileProvider state) => state.leftScreenIndex);

    Widget child;
    switch (screenIndex) {
      case 1:
        child = LeftBlock1(
          key: ValueKey(1),
        );
        break;
      case 2:
        child = LeftBlock2(
          key: ValueKey(2),
        );
        break;
      case 3:
        child = LeftBlock4(
          key: ValueKey(3),
        );
        break;
      case 0:
      default:
        child = LeftBlock3(
          key: ValueKey(0),
        );
    }

    return AnimatedSwitcher(
      duration: Duration(milliseconds: 700),
      transitionBuilder: (Widget child, Animation<double> animation) {
        return FadeTransition(
          opacity: animation,
          child: child,
        );
      },
      child: child,
    );
  }
}
