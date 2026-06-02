import '../../widgets/state_view_widget.dart';
import 'one_switch_view.dart';

class OneSwitch extends StateView<OneSwitchState> {
  final int switchIndex;

  OneSwitch({super.key, required this.switchIndex})
      : super(
          stateBuilder: (context) => OneSwitchState(context),
          view: OneSwitchView(),
        );
}

class OneSwitchState extends StateProvider<OneSwitch> {
  OneSwitchState(super.context);

  int get switchIndex => widget.switchIndex;
}
