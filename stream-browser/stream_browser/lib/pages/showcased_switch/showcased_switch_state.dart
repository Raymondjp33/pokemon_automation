import '../../widgets/state_view_widget.dart';
import 'showcased_switch_view.dart';

class ShowcasedSwitch extends StateView<ShowcasedSwitchState> {
  ShowcasedSwitch({super.key})
      : super(
          stateBuilder: (context) => ShowcasedSwitchState(context),
          view: ShowcasedSwitchView(),
        );
}

class ShowcasedSwitchState extends StateProvider<ShowcasedSwitch> {
  ShowcasedSwitchState(super.context);
}
