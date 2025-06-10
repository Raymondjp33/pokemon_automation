import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../../../services/file_provider.dart';
import 'right_block1.dart';
import 'right_block2.dart';
import 'right_block3.dart';

class RightSwitchContent extends StatelessWidget {
  const RightSwitchContent({super.key});

  @override
  Widget build(BuildContext context) {
    int screenIndex = context.select((FileProvider state) => state.screenIndex);

    Widget child;
    switch (screenIndex) {
      case 1:
        child = RightBlock1(
          key: ValueKey(1),
        );
        break;
      case 2:
        child = RightBlock3(
          key: ValueKey(2),
        );
        break;
      case 0:
      default:
        child = RightBlock2(
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
