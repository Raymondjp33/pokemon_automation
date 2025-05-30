import 'package:json_annotation/json_annotation.dart';

part 'target.model.g.dart';

@JsonSerializable(explicitToJson: true)
class TargetModel {
  String name;
  int target;
  String dexNum;

  @JsonKey(name: 'main_target')
  bool mainTarget;

  TargetModel({
    required this.name,
    required this.target,
    required this.dexNum,
    this.mainTarget = false,
  });

  factory TargetModel.fromJson(Map<String, dynamic>? json) {
    if (json == null) throw Exception('TargetModel: json was null');
    try {
      return _$TargetModelFromJson(json);
    } catch (e, stack) {
      throw 'TargetModel.fromJson: $e, $stack';
    }
  }

  Map<String, dynamic> toJson() {
    Map<String, dynamic> json = _$TargetModelToJson(this);
    return json;
  }
}
